import time
import random
from utils.config_loader import load_config

def random_wait():
    config = load_config()
    min_wait = config["wait_range_seconds"]["min"]
    max_wait = config["wait_range_seconds"]["max"]
    delay = random.uniform(min_wait, max_wait)
    print(f"[WAIT] Sleeping for {delay:.2f} seconds...")
    time.sleep(delay)