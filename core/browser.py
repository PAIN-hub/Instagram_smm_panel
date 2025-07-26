from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import random
from utils.config_loader import load_config
import os

def launch_browser(proxy=None, headless=False):
    config = load_config()
    
    # Load user-agent list
    user_agent = None
    if config.get('use_random_user_agent', False):
        with open("config/user_agents.txt") as f:
            user_agents = [ua.strip() for ua in f.readlines()]
            user_agent = random.choice(user_agents)

    try:
        playwright = sync_playwright().start()
        args = []

        if proxy:
            args.append(f"--proxy-server={proxy}")

        browser = playwright.chromium.launch(headless=headless, args=args)

        context = browser.new_context(
            user_agent=user_agent or "Mozilla/5.0 (iPhone; CPU iPhone OS 13_6_1 like Mac OS X)...",  # fallback
            viewport={"width": 375, "height": 667},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            locale="en-US"
        )

        page = context.new_page()
        page.set_default_timeout(60000)

        print("[+] Navigating to Instagram signup page...")
        page.goto("https://www.instagram.com/accounts/emailsignup/", timeout=60000)

        return context, page

    except PlaywrightTimeout:
        print("[-] Timeout while loading the page.")
        raise

    except Exception as e:
        print(f"[-] Failed to launch browser: {e}")
        raise