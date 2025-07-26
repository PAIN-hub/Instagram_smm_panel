import time
import requests
from utils.logger import logger
from utils.config_loader import load_config

class CaptchaSolver:
    def __init__(self):
        self.api_key = load_config()["captcha_api_key"]
        self.base_url = "https://api.capmonster.cloud"

    def is_captcha_present(self, page):
        return "captcha" in page.content().lower()

    def solve(self, page):
        if not self.is_captcha_present(page):
            logger.info("[CAPTCHA] No captcha detected.")
            return

        logger.info("[CAPTCHA] Captcha detected. Sending to CapMonster...")

        task_payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": "https://www.instagram.com/accounts/emailsignup/",
                "websiteKey": self._extract_sitekey(page)
            }
        }

        task_id = self._create_task(task_payload)
        token = self._wait_for_result(task_id)

        if token:
            logger.info("[CAPTCHA] Token received. Injecting...")
            page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{token}";')
            page.evaluate('''() => {
                document.querySelector('form').submit();
            }''')
        else:
            raise Exception("Captcha solving failed.")

    def _create_task(self, payload):
        response = requests.post(f"{self.base_url}/createTask", json=payload)
        response.raise_for_status()
        task_id = response.json().get("taskId")
        if not task_id:
            raise Exception("Failed to create captcha task")
        return task_id

    def _wait_for_result(self, task_id, timeout=120):
        elapsed = 0
        while elapsed < timeout:
            response = requests.post(f"{self.base_url}/getTaskResult", json={
                "clientKey": self.api_key,
                "taskId": task_id
            })
            result = response.json()
            if result["status"] == "ready":
                return result["solution"]["gRecaptchaResponse"]
            time.sleep(5)
            elapsed += 5
        raise TimeoutError("Captcha solving timed out")

    def _extract_sitekey(self, page):
        content = page.content()
        start = content.find('data-sitekey="') + len('data-sitekey="')
        end = content.find('"', start)
        sitekey = content[start:end]
        logger.info(f"[CAPTCHA] Found sitekey: {sitekey}")
        return sitekey