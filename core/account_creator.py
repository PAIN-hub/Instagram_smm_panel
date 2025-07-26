from core.browser import launch_browser
from core.human_behavior import simulate_typing, random_wait
from utils.sms_handler import SMSHandler
from utils.captcha_solver import CaptchaSolver
from utils.email_verifier import EmailVerifier
from utils.logger import logger
import time

class AccountCreator:
    def __init__(self, username, password, email, proxy=None, headless=False):
        self.username = username
        self.password = password
        self.email = email
        self.proxy = proxy
        self.headless = headless
        self.sms = SMSHandler()
        self.email_verifier = EmailVerifier()
        self.captcha = CaptchaSolver()

    def run(self):
        try:
            context, page = launch_browser(proxy=self.proxy, headless=self.headless)
            logger.info("Browser launched, navigating to signup page...")
            page.goto("https://www.instagram.com/accounts/emailsignup/", timeout=60000)
            random_wait()

            logger.info("Filling the signup form...")

            # Fill email
            simulate_typing(page, 'input[name="emailOrPhone"]', self.email)
            random_wait()

            # Full name (fake)
            simulate_typing(page, 'input[name="fullName"]', "John IGAuto")
            random_wait()

            # Username
            simulate_typing(page, 'input[name="username"]', self.username)
            random_wait()

            # Password
            simulate_typing(page, 'input[name="password"]', self.password)
            random_wait()

            # Click Next button
            page.click('button[type="submit"]')
            random_wait()

            # Captcha solving
            if self.captcha.is_captcha_present(page):
                self.captcha.solve(page)

            # Phone number verification
            phone_number, request_id = self.sms.get_number()
            logger.info(f"Using phone number: {phone_number}")
            page.fill('input[name="emailOrPhone"]', phone_number)
            page.click('button[type="submit"]')
            random_wait()

            code = self.sms.wait_for_code(request_id)
            page.fill('input[name="confirmationCode"]', code)
            page.click('button[type="submit"]')
            logger.info("Phone verified.")

            # Email Verification
            logger.info("Waiting for email verification link...")
            verify_url = self.email_verifier.get_verification_link(self.email)
            page.goto(verify_url)
            logger.info("Email verified.")

            logger.info(f"✅ IG Account Created: {self.username} | {self.password}")

            # Save to success log
            with open("logs/success.log", "a") as f:
                f.write(f"{self.username}:{self.password}:{self.email}\n")

            context.close()

        except Exception as e:
            logger.error(f"❌ Account creation failed: {e}")
            with open("logs/error.log", "a") as f:
                f.write(f"{self.username}:{self.email} => {str(e)}\n")