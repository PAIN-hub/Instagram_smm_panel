import argparse
import utils.proxy_scraper  # Automatically scrapes and saves fresh proxies
import threading
import time
from core.account_creator import AccountCreator
from utils.logger import setup_logger, log_info, log_error
from utils.helper import generate_unique_credentials  # We'll define this soon


def create_account_instance(proxy, headless):
    try:
        username, password, email = generate_unique_credentials()
        creator = AccountCreator(
            username=username,
            password=password,
            email=email,
            proxy=proxy,
            headless=headless,
        )
        creator.run()
        log_info(f"Successfully created account: {username}")
    except Exception as e:
        log_error(f"[ERROR] Failed to create account: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Instagram Account Creator Bot")
    parser.add_argument("--proxy", help="Use a specific proxy or path to proxy list")
    parser.add_argument(
        "--threads", type=int, default=1, help="Number of parallel threads"
    )
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    args = parser.parse_args()

    setup_logger()

    threads = []

    for _ in range(args.threads):
        t = threading.Thread(
            target=create_account_instance, args=(args.proxy, args.headless)
        )
        t.start()
        threads.append(t)
        time.sleep(2)  # slight delay to avoid spam-burst

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
