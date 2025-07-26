# 🚀 Instagram SMM Panel

🔥 Fully automated Instagram bot that creates accounts, solves captchas, verifies with email/SMS, and performs actions like follow, like, and comment.  
Supports proxy rotation, headless mode, and one-click setup. Built for devs, testers, and bot researchers.

---

## 📸 Overview

An all-in-one tool that:

- Automates Instagram account creation
- Solves captchas using **CapMonster** / **AntiCaptcha**
- Verifies emails via **Mail.tm** / **1secmail**
- Handles SMS activation through **SMS-Activate**
- Randomizes user agents and rotates proxies
- Auto-scrapes fresh proxies from `sslproxies.org`
- Performs post-registration actions: **Follow**, **Like**, **Comment**
- Controlled through `settings.yaml` with full logging and error tracking

---

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/veerusjondy/instagram_smm_panel.git
cd instagram_smm_panel

2. Run one-click setup

python setup_launcher.py

Everything gets auto-generated. No manual config editing needed.


```
📁 Project Structure

instagram_account_creator/
├── main.py                         # Account creation logic
├── launch_accounts_to_engage.py   # Engagement engine
├── setup_launcher.py              # One-click installer
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


---

✅ Features

[x] Account creation via Playwright

[x] Captcha solving (CapMonster, AntiCaptcha ready)

[x] Email verification (Mail.tm, 1secmail)

[x] SMS activation (SMS-Activate)

[x] Random user-agents + proxy rotation

[x] Proxy scraping from sslproxies.org

[x] Post-registration actions: Follow, Like, Comment

[x] Full logging system with success/error tracking

[x] Configurable with a single settings.yaml



---

🧠 To-Do

[ ] GUI Launcher

[ ] Cloud CAPTCHA API support

[ ] CSV import/export

[ ] Docker deployment support


📜 License

MIT License
Free to use and modify for ethical automation purposes only.


🤝 Contributing

Pull requests welcome.
Fork it, build something wild, and send it back.


Built with ❤️ by @veerusjondy