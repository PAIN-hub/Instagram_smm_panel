import time
import threading
import traceback
import random
from django.utils import timezone
from django.db import connection
from panel.models import BotTask, InstagramAccount, Proxy
from panel.bot_logic.account_creator import AccountCreator
from panel.bot_logic.browser import launch_browser
from panel.bot_logic.social_actions import instagram_login, follow_user, like_latest_post, comment_on_post
from panel.bot_logic.helper import generate_unique_credentials
from panel.bot_logic.settings_helper import get_setting

# Global lock and worker state tracking
_worker_thread = None
_worker_running = False

def start_worker_thread():
    """
    Spawns the background daemon thread worker if it is not already running.
    """
    global _worker_thread, _worker_running
    if _worker_thread is not None and _worker_thread.is_alive():
        return
        
    _worker_running = True
    _worker_thread = threading.Thread(target=worker_loop, daemon=True, name="SMM_Worker_Thread")
    _worker_thread.start()
    print("[WORKER] Background queue worker thread started.")

def stop_worker_thread():
    global _worker_running
    _worker_running = False
    print("[WORKER] Stop signal sent to worker thread.")

def worker_loop():
    while _worker_running:
        try:
            # Atomically query and claim the next pending task
            pending_task = BotTask.objects.filter(status='pending').order_by('created_at').first()
            
            if pending_task:
                claimed = BotTask.objects.filter(id=pending_task.id, status='pending').update(
                    status='running',
                    started_at=timezone.now()
                )
                if claimed > 0:
                    task = BotTask.objects.get(id=pending_task.id)
                    process_task(task)
            else:
                time.sleep(2) # No tasks, sleep for a short interval
                
        except Exception as e:
            print(f"[WORKER] Error in main loop: {e}")
            time.sleep(3)
        finally:
            # Clean up Django database connections in long-running threads
            connection.close()

def process_task(task: BotTask):
    task.logs = f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | Task marked RUNNING.\n"
    task.save()

    log_acc = task.logs

    def log(msg):
        nonlocal log_acc
        log_acc += f"{timezone.now().strftime('%Y-%m-%d %H:%M:%S')} | {msg}\n"
        task.logs = log_acc
        task.save()
        print(f"[TASK-{task.id}] {msg}")

    try:
        # Determine Proxy to use
        proxy_url = None
        proxy_obj = None
        
        # If the account has a proxy, use it
        if task.account and task.account.proxy:
            proxy_obj = task.account.proxy
        # Otherwise, check if we should rotate and pick an active, non-blocked proxy from DB
        elif get_setting("rotate_proxies", "True").lower() == 'true':
            # Prioritize verified clean proxies first
            proxy_obj = Proxy.objects.filter(is_active=True, health_status='clean').order_by('?').first()
            if not proxy_obj:
                # Fallback to untested active proxies (excluding blocked/offline)
                proxy_obj = Proxy.objects.filter(is_active=True).exclude(health_status__in=['blocked', 'offline']).order_by('?').first()

        if proxy_obj:
            auth_part = f"{proxy_obj.username}:{proxy_obj.password}@" if proxy_obj.username and proxy_obj.password else ""
            proxy_url = f"{proxy_obj.protocol}://{auth_part}{proxy_obj.ip}:{proxy_obj.port}"
            log(f"Using proxy: {proxy_obj.ip}:{proxy_obj.port}")

        if task.task_type == 'create_account':
            log("Initializing account creation sequence...")
            
            # Generate unique credentials
            username, password, email = generate_unique_credentials()
            
            creator = AccountCreator(
                username=username,
                password=password,
                email=email,
                proxy=proxy_url,
                task=task
            )
            # creator.run() updates the task logs and creates the InstagramAccount model row
            creator.run()
            
            # Link created account to the task
            try:
                created_acc = InstagramAccount.objects.get(username=username)
                task.account = created_acc
                
                # Assign proxy to the account
                if proxy_obj:
                    created_acc.proxy = proxy_obj
                    created_acc.save()
            except Exception:
                pass
                
        else:
            # Engagement Tasks: Follow, Like, Comment
            if not task.account:
                raise ValueError("An Instagram account must be specified for engagement tasks.")
                
            account = task.account
            log(f"Executing engagement action using account @{account.username}...")
            
            playwright_instance = None
            browser = None
            context = None
            page = None
            try:
                # Launch browser
                playwright_instance, browser, context, page = launch_browser(
                    proxy=proxy_url,
                    headless=None
                )
                
                # Log in
                logged_in = instagram_login(page, account.username, account.password, logger=log)
                if not logged_in:
                    account.status = 'verification_needed'
                    account.save()
                    raise Exception("Authentication failed on Instagram login page.")
                    
                # Perform action
                success = False
                if task.task_type == 'follow':
                    success = follow_user(page, task.target, logger=log)
                elif task.task_type == 'like':
                    success = like_latest_post(page, task.target, logger=log)
                elif task.task_type == 'comment':
                    if not task.comment_text:
                        task.comment_text = "Nice post! 🔥"
                    success = comment_on_post(page, task.target, task.comment_text, logger=log)
                    
                if not success:
                    raise Exception(f"Action '{task.get_task_type_display()}' was executed but returned failure state.")
                    
                # Update account last used
                account.last_used = timezone.now()
                account.save()
            finally:
                # Ensure all browser resources are safely terminated
                if page:
                    try: page.close()
                    except Exception: pass
                if context:
                    try: context.close()
                    except Exception: pass
                if browser:
                    try: browser.close()
                    except Exception: pass
                if playwright_instance:
                    try: playwright_instance.stop()
                    except Exception: pass

        # Mark task completed
        task.status = 'completed'
        task.completed_at = timezone.now()
        log("Task completed successfully.")
        
    except Exception as e:
        task.status = 'failed'
        task.error_message = str(e)
        task.completed_at = timezone.now()
        log(f"Task failed: {e}\n{traceback.format_exc()}")
        task.save()
