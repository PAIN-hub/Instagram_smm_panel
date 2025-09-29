# Instagram SMM Panel

🔥 A fully automated Instagram bot that streamlines account creation, solves captchas, verifies accounts via email/SMS, and performs key engagement actions like following, liking, and commenting.  
Supports proxy rotation, headless mode, and one-click setup. Designed for developers, testers, and bot researchers.

---

## Overview

Instagram SMM Panel is an all-in-one automation tool that:

- Automates Instagram account creation
- Solves captchas using **CapMonster** or **AntiCaptcha**
- Verifies emails via **Mail.tm** or **1secmail**
- Handles SMS activation through **SMS-Activate**
- Randomizes user agents and rotates proxies
- Auto-scrapes fresh proxies from `sslproxies.org`
- Performs post-registration actions: **Follow**, **Like**, **Comment**
- Is fully configurable via `settings.yaml`, with comprehensive logging and error tracking

---

## 🛠️ Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/pain-hub/instagram_smm_panel.git
cd instagram_smm_panel
```

### 2. One-Click Setup

```bash
python setup_launcher.py
```

Everything is auto-generated for you—no manual configuration required!

---

## Project Structure

```bash
instagram_account_creator/
├── main.py                         # Account creation logic
├── launch_accounts_to_engage.py    # Engagement engine
├── setup_launcher.py               # One-click installer
├── requirements.txt
├── README.md

├── config/
│   ├── proxies.txt
│   ├── user_agents.txt
│   ├── settings.yaml
│   └── targets.txt                # List of users to engage with

├── core/
│   ├── browser.py
│   ├── account_creator.py
│   ├── human_behavior.py
│   └── dashboard.py

├── utils/
│   ├── captcha_solver.py
│   ├── sms_handler.py
│   ├── email_verifier.py
│   ├── logger.py
│   ├── proxy_scraper.py
│   └── proxy_generator.py

├── logs/
│   ├── success.log
│   └── error.log
```

---

## Features

- ✔️ Account creation via Playwright
- ✔️ Captcha solving (CapMonster, AntiCaptcha ready)
- ✔️ Email verification (Mail.tm, 1secmail)
- ✔️ SMS activation (SMS-Activate)
- ✔️ Random user-agents & proxy rotation
- ✔️ Proxy scraping from sslproxies.org
- ✔️ Post-registration actions: Follow, Like, Comment
- ✔️ Full logging system with success/error tracking
- ✔️ Configuration with a single settings.yaml

---

## Roadmap

- [ ] GUI Launcher
- [ ] Cloud CAPTCHA API support
- [ ] CSV import/export
- [ ] Docker deployment support

---

## License

MIT License  
Free to use and modify for ethical automation purposes only.

---

## Contributing

Pull requests are welcome!  
Fork it, build something cool, and send it back.

---

## Business Inquiries

For business inquiries, please contact via Telegram: [@0x_beely](https://t.me/0x_beely)