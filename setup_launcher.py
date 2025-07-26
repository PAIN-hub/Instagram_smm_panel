# setup_launcher.py
import os
import subprocess
import sys

REQUIREMENTS = "requirements.txt"
CONFIG_FILES = [
    "config/proxies.txt",
    "config/user_agents.txt",
    "config/settings.yaml",
    "config/targets.txt"
]

def install_requirements():
    print("[+] Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS])

def fetch_proxies():
    print("[+] Fetching fresh proxies...")
    import utils.proxy_scraper  # auto-scrapes on import

def ensure_config_files():
    os.makedirs("config", exist_ok=True)
    for file in CONFIG_FILES:
        if not os.path.exists(file):
            with open(file, "w") as f:
                if file.endswith(".yaml"):
                    f.write("""captcha_service: capmonster
captcha_api_key: "YOUR_API_KEY"
sms_service: sms-activate
sms_api_key: "YOUR_API_KEY"
email_service: mailtm
use_random_user_agent: true
rotate_proxies: true
wait_range_seconds:
  min: 2
  max: 6
default_proxy: ""
""")
                else:
                    f.write("# Auto-generated\n")

def run_main_bot():
    print("[+] Launching account creator bot...")
    subprocess.call([sys.executable, "main.py"])

def run_engage_bot():
    print("[+] Launching engagement bot...")
    subprocess.call([sys.executable, "launch_accounts_to_engage.py"])

def main():
    install_requirements()
    ensure_config_files()
    fetch_proxies()
    run_main_bot()
    run_engage_bot()

if __name__ == "__main__":
    main()
