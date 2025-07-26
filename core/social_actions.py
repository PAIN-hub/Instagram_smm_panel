from playwright.sync_api import Page
import time


def follow_user(page: Page, username: str):
    page.goto(f"https://www.instagram.com/{username}/")
    try:
        page.wait_for_selector('text="Follow"', timeout=5000)
        page.click('text="Follow"')
        print(f"[ACTION] Followed @{username}")
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] Failed to follow @{username}: {e}")


def like_latest_post(page: Page, username: str):
    page.goto(f"https://www.instagram.com/{username}/")
    try:
        page.wait_for_selector('article a', timeout=5000)
        page.click('article a')
        page.wait_for_selector('svg[aria-label="Like"]', timeout=5000)
        page.click('svg[aria-label="Like"]')
        print(f"[ACTION] Liked post from @{username}")
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] Failed to like @{username}'s post: {e}")


def comment_on_post(page: Page, username: str, message: str):
    page.goto(f"https://www.instagram.com/{username}/")
    try:
        page.wait_for_selector('article a', timeout=5000)
        page.click('article a')
        page.wait_for_selector('textarea', timeout=5000)
        page.fill('textarea', message)
        page.click('text="Post"')
        print(f"[ACTION] Commented on @{username}: {message}")
        time.sleep(2)
    except Exception as e:
        print(f"[ERROR] Failed to comment on @{username}'s post: {e}")


def load_targets(file_path="config/targets.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"[ERROR] Could not load targets: {e}")
        return []


def get_proxy_list(file_path="config/proxies.txt"):
    try:
        with open(file_path, "r") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"[ERROR] Could not load proxies: {e}")
        return []