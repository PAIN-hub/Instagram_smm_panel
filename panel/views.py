import csv
import io
import threading
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.db.models import Count
from django.utils import timezone
from django.conf import settings
from datetime import timedelta

from panel.models import InstagramAccount, Proxy, EngagementTarget, BotTask
from panel.forms import AccountForm, ProxyForm, TargetForm, TaskForm, ImportCSVForm, SettingsForm
from panel.bot_logic.settings_helper import get_all_settings, set_setting
from panel.bot_logic.proxy_scraper import scrape_sslproxies, test_proxy, test_all_proxies_concurrently
from panel.worker import start_worker_thread

def ensure_worker():
    """
    Ensures that the background queue worker thread is alive.
    """
    start_worker_thread()

# ----------------- Dashboard View -----------------
def dashboard(request):
    ensure_worker()
    
    # Calculate Card metrics
    total_accounts = InstagramAccount.objects.count()
    active_accounts = InstagramAccount.objects.filter(status='active').count()
    banned_accounts = InstagramAccount.objects.filter(status='banned').count()
    needs_verify = InstagramAccount.objects.filter(status='verification_needed').count()
    
    total_proxies = Proxy.objects.count()
    active_proxies = Proxy.objects.filter(is_active=True).count()
    
    total_tasks = BotTask.objects.count()
    running_tasks = BotTask.objects.filter(status='running').count()
    pending_tasks = BotTask.objects.filter(status='pending').count()
    completed_tasks = BotTask.objects.filter(status='completed').count()
    failed_tasks = BotTask.objects.filter(status='failed').count()
    
    # Task success metrics for charts
    tasks_by_status = list(
        BotTask.objects.values('status')
        .annotate(count=Count('status'))
    )
    
    # Recent tasks list
    recent_tasks = BotTask.objects.order_by('-created_at')[:8]
    
    context = {
        'total_accounts': total_accounts,
        'active_accounts': active_accounts,
        'banned_accounts': banned_accounts,
        'needs_verify': needs_verify,
        'total_proxies': total_proxies,
        'active_proxies': active_proxies,
        'total_tasks': total_tasks,
        'running_tasks': running_tasks,
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'failed_tasks': failed_tasks,
        'recent_tasks': recent_tasks,
        'tasks_by_status': tasks_by_status,
        'nav': 'dashboard'
    }
    return render(request, 'panel/dashboard.html', context)

# ----------------- Accounts Manager -----------------
def accounts_list(request):
    ensure_worker()
    accounts = InstagramAccount.objects.all().order_by('-created_at')
    
    # Forms
    account_form = AccountForm()
    csv_form = ImportCSVForm()
    
    if request.method == 'POST':
        if 'add_account' in request.POST:
            form = AccountForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account added successfully.")
                return redirect('accounts_list')
            else:
                messages.error(request, "Failed to add account. Check input details.")
                account_form = form
                
        elif 'import_csv' in request.POST:
            form = ImportCSVForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                try:
                    data = csv_file.read().decode('utf-8')
                    io_string = io.StringIO(data)
                    reader = csv.reader(io_string)
                    # Skip header if present
                    header = next(reader, None)
                    has_header = False
                    if header and any(h.lower() in ['username', 'password', 'email'] for h in header):
                        has_header = True
                    else:
                        # Re-read from beginning if no header detected
                        io_string.seek(0)
                        reader = csv.reader(io_string)
                        
                    imported_count = 0
                    for row in reader:
                        # expected format: username,password,email,email_password(opt),phone(opt)
                        if len(row) >= 3:
                            username = row[0].strip()
                            password = row[1].strip()
                            email = row[2].strip()
                            email_password = row[3].strip() if len(row) > 3 else ""
                            phone = row[4].strip() if len(row) > 4 else ""
                            
                            InstagramAccount.objects.update_or_create(
                                username=username,
                                defaults={
                                    'password': password,
                                    'email': email,
                                    'email_password': email_password,
                                    'phone': phone,
                                    'status': 'active'
                                }
                            )
                            imported_count += 1
                    messages.success(request, f"Imported {imported_count} accounts from CSV.")
                except Exception as e:
                    messages.error(request, f"Failed to parse CSV file: {e}")
                return redirect('accounts_list')
                
    context = {
        'accounts': accounts,
        'account_form': account_form,
        'csv_form': csv_form,
        'nav': 'accounts'
    }
    return render(request, 'panel/accounts.html', context)

def delete_account(request, account_id):
    account = get_object_or_404(InstagramAccount, pk=account_id)
    username = account.username
    account.delete()
    messages.success(request, f"Account @{username} deleted successfully.")
    return redirect('accounts_list')

def export_accounts_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="smm_accounts_{timezone.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['username', 'password', 'email', 'email_password', 'phone', 'status', 'created_at'])
    
    accounts = InstagramAccount.objects.all()
    for acc in accounts:
        writer.writerow([
            acc.username, 
            acc.password, 
            acc.email, 
            acc.email_password, 
            acc.phone, 
            acc.status, 
            acc.created_at.isoformat()
        ])
    return response

def trigger_create_account_task(request):
    # Enqueue a task to create a new account
    BotTask.objects.create(task_type='create_account')
    messages.success(request, "Enqueued account creation task. Worker is processing.")
    return redirect('tasks_list')

# ----------------- Proxies Manager -----------------
def proxies_list(request):
    ensure_worker()
    proxies = Proxy.objects.all().order_by('-created_at')
    proxy_form = ProxyForm()
    
    if request.method == 'POST':
        if 'add_proxy' in request.POST:
            form = ProxyForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Proxy added successfully.")
                return redirect('proxies_list')
            else:
                messages.error(request, "Failed to add proxy. Check input fields.")
                proxy_form = form
                
    context = {
        'proxies': proxies,
        'proxy_form': proxy_form,
        'nav': 'proxies'
    }
    return render(request, 'panel/proxies.html', context)

def delete_proxy(request, proxy_id):
    proxy = get_object_or_404(Proxy, pk=proxy_id)
    address = f"{proxy.ip}:{proxy.port}"
    proxy.delete()
    messages.success(request, f"Proxy {address} deleted successfully.")
    return redirect('proxies_list')

def trigger_scrape_proxies(request):
    def run_scrape():
        scrape_sslproxies()
    
    threading.Thread(target=run_scrape, daemon=True).start()
    messages.success(request, "Started background proxy scraping from sslproxies.org...")
    return redirect('proxies_list')

def trigger_test_proxies(request):
    proxy_ids = list(Proxy.objects.values_list('id', flat=True))
    def run_tests():
        test_all_proxies_concurrently(proxy_ids=proxy_ids)
            
    threading.Thread(target=run_tests, daemon=True).start()
    messages.success(request, f"Parallel Instagram health checks launched for {len(proxy_ids)} proxies in the background.")
    return redirect('proxies_list')

def test_single_proxy(request, proxy_id):
    proxy = get_object_or_404(Proxy, pk=proxy_id)
    is_active, status = test_proxy(proxy)
    if is_active:
        messages.success(request, f"Proxy {proxy.ip}:{proxy.port} is {proxy.get_health_status_display()} ({proxy.speed}s latency).")
    else:
        err = f" - {proxy.error_message}" if proxy.error_message else ""
        messages.warning(request, f"Proxy {proxy.ip}:{proxy.port} is {proxy.get_health_status_display()}{err}.")
    return redirect('proxies_list')

# ----------------- Targets Manager -----------------
def targets_list(request):
    ensure_worker()
    targets = EngagementTarget.objects.all().order_by('-created_at')
    target_form = TargetForm()
    
    if request.method == 'POST':
        if 'add_target' in request.POST:
            form = TargetForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, f"Target @{form.cleaned_data['username']} added successfully.")
                return redirect('targets_list')
            else:
                messages.error(request, "Failed to add target profile.")
                target_form = form
                
    context = {
        'targets': targets,
        'target_form': target_form,
        'nav': 'targets'
    }
    return render(request, 'panel/targets.html', context)

def delete_target(request, target_id):
    target = get_object_or_404(EngagementTarget, pk=target_id)
    username = target.username
    target.delete()
    messages.success(request, f"Target @{username} removed.")
    return redirect('targets_list')

# ----------------- Tasks Manager -----------------
def tasks_list(request):
    ensure_worker()
    tasks = BotTask.objects.all().order_by('-created_at')
    task_form = TaskForm()
    
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Enqueued bot task successfully.")
            return redirect('tasks_list')
        else:
            messages.error(request, "Failed to enqueue task. Check your fields.")
            task_form = form
            
    context = {
        'tasks': tasks,
        'task_form': task_form,
        'nav': 'tasks'
    }
    return render(request, 'panel/tasks.html', context)

def cancel_task(request, task_id):
    task = get_object_or_404(BotTask, pk=task_id)
    if task.status == 'pending':
        task.delete()
        messages.success(request, "Task cancelled and removed from queue.")
    else:
        messages.error(request, "Only pending tasks can be cancelled.")
    return redirect('tasks_list')

def clear_tasks(request):
    deleted = BotTask.objects.exclude(status='running').delete()
    messages.success(request, f"Removed {deleted[0]} completed, pending, and failed tasks from log history.")
    return redirect('tasks_list')

def task_detail(request, task_id):
    ensure_worker()
    task = get_object_or_404(BotTask, pk=task_id)
    context = {
        'task': task,
        'nav': 'tasks'
    }
    return render(request, 'panel/task_detail.html', context)

def get_task_logs(request, task_id):
    task = get_object_or_404(BotTask, pk=task_id)
    return JsonResponse({
        'status': task.status,
        'completed': task.status in ['completed', 'failed'],
        'logs': task.logs,
        'error_message': task.error_message or ''
    })

# ----------------- Settings Manager -----------------
def settings_view(request):
    ensure_worker()
    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            for key, val in form.cleaned_data.items():
                set_setting(key, val)
            messages.success(request, "Global system configurations saved.")
            return redirect('settings_view')
        else:
            messages.error(request, "Failed to save settings. Review validation errors.")
    else:
        initial_data = get_all_settings()
        # Convert string booleans to actual booleans for checkboxes
        initial_data['use_random_user_agent'] = initial_data.get('use_random_user_agent', 'True').lower() == 'true'
        initial_data['rotate_proxies'] = initial_data.get('rotate_proxies', 'True').lower() == 'true'
        initial_data['headless_mode'] = initial_data.get('headless_mode', 'True').lower() == 'true'
        
        form = SettingsForm(initial=initial_data)
        
    context = {
        'form': form,
        'nav': 'settings'
    }
    return render(request, 'panel/settings.html', context)
