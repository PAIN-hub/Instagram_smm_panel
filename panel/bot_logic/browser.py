import os
import shutil
import random
from playwright.sync_api import sync_playwright
from panel.bot_logic.settings_helper import get_setting

DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]

def find_system_chromium():
    """
    Looks for installed system Chrome or Chromium binaries.
    """
    candidates = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
    ]
    for c in candidates:
        if c and os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return None

def launch_browser(proxy=None, headless=None, playwright_instance=None):
    """
    Launches a browser instance based on database configurations with fallback protection.
    Returns: (playwright_instance, browser, context, page)
    """
    browser_type_name = get_setting('browser_type', 'chromium').lower()
    browser_path = get_setting('browser_path', '').strip()
    
    if headless is None:
        headless = get_setting('headless_mode', 'True').lower() == 'true'

    use_random_ua = get_setting('use_random_user_agent', 'True').lower() == 'true'
    user_agent = random.choice(DEFAULT_USER_AGENTS) if use_random_ua else DEFAULT_USER_AGENTS[0]

    p = playwright_instance or sync_playwright().start()
    
    launch_kwargs = {
        "headless": headless,
        "timeout": 30000,
    }
    
    # Chromium args for stability on Linux/servers and anti-detection
    chromium_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
        "--disable-infobars",
        "--no-first-run",
        "--no-default-browser-check",
    ]

    # Handle proxy configurations
    if proxy:
        if isinstance(proxy, str):
            launch_kwargs["proxy"] = {"server": proxy}
        elif isinstance(proxy, dict):
            launch_kwargs["proxy"] = proxy

    browser = None

    # Determine custom executable if specified and valid
    if browser_path and os.path.exists(browser_path):
        # Prevent passing stock Firefox to Playwright (causes Juggler hang)
        if browser_type_name == 'firefox' and ('/usr/bin/firefox' in browser_path or 'firefox-esr' in browser_path):
            print(f"[BROWSER] Notice: Stock system Firefox ({browser_path}) is incompatible with Playwright Juggler. Using Playwright managed Firefox or Chromium fallback.")
        else:
            launch_kwargs["executable_path"] = browser_path
            print(f"[BROWSER] Using custom executable: {browser_path}")

    # Launch browser according to config type
    print(f"[BROWSER] Attempting to launch {browser_type_name.upper()} (headless={headless})...")
    
    if browser_type_name == 'firefox':
        try:
            browser = p.firefox.launch(**launch_kwargs)
        except Exception as e:
            print(f"[BROWSER] Firefox launch failed: {e}. Falling back to Chromium...")
            browser_type_name = 'chromium'
            launch_kwargs.pop("executable_path", None)

    if browser is None:
        # Chromium launch
        launch_kwargs["args"] = chromium_args
        if "executable_path" not in launch_kwargs:
            sys_chrome = find_system_chromium()
            if sys_chrome:
                launch_kwargs["executable_path"] = sys_chrome
                print(f"[BROWSER] Using detected system browser: {sys_chrome}")
        try:
            browser = p.chromium.launch(**launch_kwargs)
        except Exception as e:
            # If system executable fails, try without custom executable_path
            if "executable_path" in launch_kwargs:
                print(f"[BROWSER] Custom chromium launch error ({e}). Retrying with default Playwright binary...")
                launch_kwargs.pop("executable_path", None)
                browser = p.chromium.launch(**launch_kwargs)
            else:
                raise e

    context = browser.new_context(
        user_agent=user_agent,
        viewport={"width": 390, "height": 844},
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        locale="en-US",
        timezone_id="America/New_York",
        permissions=["geolocation", "notifications"],
        extra_http_headers={
            "Accept-Language": "en-US,en;q=0.9",
        }
    )

    page = context.new_page()
    page.set_default_timeout(45000)

    # Anti-bot detection stealth evasion
    try:
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            window.chrome = { runtime: {} };
        """)
    except Exception:
        pass

    return p, browser, context, page
