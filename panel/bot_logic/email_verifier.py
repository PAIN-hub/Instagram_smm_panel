import time
import requests
import random
import string
import re
from panel.bot_logic.settings_helper import get_setting

class EmailVerifier:
    def __init__(self, logger=None):
        self.logger = logger or print
        self.service = get_setting("email_service", "mailtm").lower()
        self.email = None
        self.password = None
        self.token = None
        self.login = None
        self.domain = None
        
        self._init_service()

    def _init_service(self):
        if self.service == "mailtm":
            try:
                self._init_mailtm()
                return
            except Exception as e:
                self.logger(f"[EMAIL] Mail.tm initialization failed ({e}). Falling back to fallback generator.")
        
        # Fallback to local random address if remote service is unavailable
        self.domain = "inboxbear.com"
        self.login = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        self.email = f"{self.login}@{self.domain}"
        self.logger(f"[EMAIL] Fallback temporary email: {self.email}")

    def _init_mailtm(self):
        headers = {"User-Agent": "Mozilla/5.0"}
        domain_resp = requests.get("https://api.mail.tm/domains", headers=headers, timeout=10)
        domain_resp.raise_for_status()
        domain_data = domain_resp.json()
        
        members = domain_data.get("hydra:member", [])
        if not members:
            raise RuntimeError("No active domains returned by Mail.tm")
            
        self.domain = members[0]["domain"]
        
        # Try creating account (with retry if username collides)
        for _ in range(3):
            self.login = random.choice(string.ascii_lowercase) + ''.join(random.choices(string.ascii_lowercase + string.digits, k=9))
            self.email = f"{self.login}@{self.domain}"
            self.password = "IGAuto_" + ''.join(random.choices(string.ascii_letters + string.digits, k=10)) + "!"

            reg_resp = requests.post(
                "https://api.mail.tm/accounts",
                json={"address": self.email, "password": self.password},
                headers=headers,
                timeout=10
            )
            if reg_resp.status_code == 201:
                break
        
        if not reg_resp or reg_resp.status_code != 201:
            reg_resp.raise_for_status()

        # Obtain authentication bearer token
        token_resp = requests.post(
            "https://api.mail.tm/token",
            json={"address": self.email, "password": self.password},
            headers=headers,
            timeout=10
        )
        token_resp.raise_for_status()
        self.token = token_resp.json().get("token")
        self.logger(f"[EMAIL] Mail.tm inbox initialized: {self.email}")

    def get_email(self):
        return self.email

    def get_verification_content(self, timeout=120):
        """
        Polls the inbox for an email from Instagram and extracts both code and URL.
        Returns: (confirmation_link, confirmation_code)
        """
        self.logger(f"[EMAIL] Polling inbox for Instagram verification on {self.email}...")
        elapsed = 0
        poll_interval = 5

        while elapsed < timeout:
            try:
                body_text = self._check_inbox()
                if body_text:
                    link = self._extract_link(body_text)
                    code = self._extract_code(body_text)
                    if link or code:
                        self.logger(f"[EMAIL] Verification detected: Code={code}, Link={link}")
                        return link, code
            except Exception as e:
                self.logger(f"[EMAIL] Polling notice: {e}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        self.logger("[EMAIL] Timeout waiting for verification message.")
        return None, None

    def get_verification_link(self, timeout=120):
        link, code = self.get_verification_content(timeout=timeout)
        if link:
            return link
        if code:
            self.logger(f"[EMAIL] Found code {code} instead of link.")
            return None
        raise TimeoutError("No verification link arrived within timeout period.")

    def get_verification_code(self, timeout=120):
        link, code = self.get_verification_content(timeout=timeout)
        if code:
            return code
        raise TimeoutError("No verification code arrived within timeout period.")

    def _check_inbox(self):
        headers = {
            "User-Agent": "Mozilla/5.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            resp = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                messages = data.get("hydra:member", [])
                if messages:
                    msg_id = messages[0]["id"]
                    msg_resp = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=10)
                    if msg_resp.status_code == 200:
                        m_data = msg_resp.json()
                        return (m_data.get("text", "") or "") + " " + (m_data.get("html", [""])[0] if isinstance(m_data.get("html"), list) and m_data.get("html") else str(m_data.get("html", "")))
        return None

    def _extract_link(self, text):
        match = re.search(r'https://(www\.)?instagram\.com/accounts/confirm_email/[^"\'\s<]+', text)
        if match:
            return match.group(0)
        return None

    def _extract_code(self, text):
        # Look for 6-digit numeric verification code in subject/body
        match = re.search(r'\b(\d{6})\b', text)
        if match:
            return match.group(1)
        return None

