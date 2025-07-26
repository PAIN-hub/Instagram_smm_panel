import time
import requests
import random
import string
from utils.logger import logger

class EmailVerifier:
    def __init__(self):
        self.domain = "1secmail.com"
        self.login = self._generate_login()
        self.email = f"{self.login}@{self.domain}"
        logger.info(f"[EMAIL] Generated email: {self.email}")

    def _generate_login(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    def get_email(self):
        return self.email

    def get_verification_link(self, timeout=120):
        logger.info("[EMAIL] Waiting for Instagram verification email...")
        elapsed = 0
        poll_interval = 5

        while elapsed < timeout:
            try:
                resp = requests.get(
                    f"https://www.1secmail.com/api/v1/",
                    params={
                        "action": "getMessages",
                        "login": self.login,
                        "domain": self.domain
                    }
                )
                messages = resp.json()
                if messages:
                    msg_id = messages[0]['id']
                    logger.info(f"[EMAIL] Mail received. Fetching ID: {msg_id}")
                    msg_resp = requests.get(
                        f"https://www.1secmail.com/api/v1/",
                        params={
                            "action": "readMessage",
                            "login": self.login,
                            "domain": self.domain,
                            "id": msg_id
                        }
                    )
                    msg_data = msg_resp.json()
                    body = msg_data.get('body', '')
                    
                    # Extract IG verification link from email body
                    link = self._extract_link(body)
                    if link:
                        logger.info(f"[EMAIL] Verification link: {link}")
                        return link

            except Exception as e:
                logger.warning(f"[EMAIL] Error polling inbox: {e}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        logger.error("[EMAIL] Timeout: No verification email received.")
        raise TimeoutError("No email verification received.")

    def _extract_link(self, text):
        # Basic IG verification link matcher
        import re
        match = re.search(r'https://instagram\.com/accounts/confirm_email/[^"\s]+', text)
        return match.group(0) if match else None