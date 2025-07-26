import csv
import os
from datetime import datetime

class AccountSaver:
    def __init__(self, filepath="logs/accounts.csv"):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["username", "password", "email", "phone", "created_at"])

    def save_account(self, username, password, email, phone):
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([username, password, email, phone, datetime.now().isoformat()])

    def load_accounts(self):
        accounts = []
        with open(self.filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                accounts.append(row)
        return accounts