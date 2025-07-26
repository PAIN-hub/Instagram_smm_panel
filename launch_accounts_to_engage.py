from playwright.sync_api import sync_playwright
from utils.account_saver import AccountSaver
from core.social_actions import follow_user, like_latest_post, comment_on_post
from utils.config_loader import load_config
import random
import time


def login(page, username, password):
    page.goto("https://www.instagram.com/accounts/login/")
    page.wait_for_selector('input[name="username"]')
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_timeout(5000)
    print(f"[LOGIN] {username} logged in successfully.")


def main():
    config = load_config()
    targets = ["cristiano", "therock", "nike"]  # or load from config/targets.txt
    saver = AccountSaver()
    accounts = saver.load_accounts()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        
        for acc in accounts:
            try:
                context = browser.new_context()
                page = context.new_page()
                
                login(page, acc["username"], acc["password"])
                
                target = random.choice(targets)
                follow_user(page, target)
                like_latest_post(page, target)
                comment_on_post(page, target, message="🔥 Nice shot!")
                
                context.close()
                time.sleep(5)
                
            except Exception as e:
                print(f"[ERROR] Account @{acc['username']} failed: {e}")


if __name__ == '__main__':
    main()