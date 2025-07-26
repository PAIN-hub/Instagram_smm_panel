import time
import requests
from utils.logger import logger
from utils.config_loader import load_config

class SMSHandler:
    def __init__(self):
        config = load_config()
        self.api_key = config["sms_api_key"]
        self.base_url = "https://5sim.net/v1/user"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_number(self):
        try:
            logger.info("[SMS] Requesting phone number from 5sim...")
            response = requests.get(
                f"{self.base_url}/buy/activation/instagram/any",
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            phone = data['phone']
            request_id = data['id']
            logger.info(f"[SMS] Got phone number: {phone}")
            return phone, request_id

        except Exception as e:
            logger.error(f"[SMS] Failed to get number: {e}")
            raise

    def wait_for_code(self, request_id, timeout=120):
        logger.info("[SMS] Waiting for SMS code...")
        elapsed = 0
        poll_interval = 5

        while elapsed < timeout:
            try:
                resp = requests.get(
                    f"{self.base_url}/check/{request_id}",
                    headers=self.headers
                )
                resp.raise_for_status()
                data = resp.json()

                if data['sms']:
                    code = data['sms'][0]['code']
                    logger.info(f"[SMS] Received code: {code}")
                    return code

            except Exception as e:
                logger.warning(f"[SMS] Error checking code: {e}")

            time.sleep(poll_interval)
            elapsed += poll_interval

        logger.error("[SMS] Timeout waiting for SMS code.")
        raise TimeoutError("No code received in time.")