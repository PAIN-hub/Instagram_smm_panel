import random
import string
import time

def generate_unique_credentials():
    timestamp = str(int(time.time()))
    username = f"user_{timestamp}_{random.randint(1000,9999)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    email = f"{username}@tempmail.dev"  # Use real temp mail API in live setup
    return username, password, email