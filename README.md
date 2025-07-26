Bet. Here's your full README.md — copy this straight into your project:


---

# Instagram SMM Panel

🔥 Fully automated Instagram bot that creates accounts, solves captchas, verifies with email/SMS, and performs actions like follow, like, and comment.  
Supports proxy rotation, headless mode, and one-click setup. Built for devs, testers, and bot researchers.

---

## 📸 Overview

An all-in-one automated tool for:

- Instagram account generation  
- Captcha solving (CapMonster, AntiCaptcha)  
- Email & SMS verification  
- Engagement actions (follow/like/comment)  
- Full proxy and user-agent rotation  
- One-click setup and modular config

---

## 🚀 Features

- ✅ Automated account creation via [Playwright](https://playwright.dev)  
- ✅ Captcha solving (CapMonster, AntiCaptcha-ready)  
- ✅ Email verification (Mail.tm, 1secmail APIs)  
- ✅ SMS activation via SMS-Activate  
- ✅ Proxy scraping from sslproxies.org + rotation  
- ✅ Random user-agent spoofing  
- ✅ Auto engagement (follow, like, comment)  
- ✅ Configurable via `settings.yaml`  
- ✅ Full logs (`logs/`) and error tracking  

---

## 🛠️ Setup

### 1. Clone the Repo
```bash
git clone https://github.com/veerusjondy/instagram_smm_panel.git
cd instagram_smm_panel

2. Run One-Click Setup

python setup_launcher.py

That’s it. No config file tinkering. The script handles everything.


---

📁 Folder Structure

instagram_account_creator/
├── main.py                         # Account creation logic
├── launch_accounts_to_engage.py   # Engagement engine
├── setup_launcher.py              # One-click installer & launcher
├── requirements.txt
├── README.md

├── config/
│   ├── proxies.txt
│   ├── user_agents.txt
│   ├── settings.yaml
│   └── targets.txt                # Target users to engage with

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

✅ To-Do

[ ] Add GUI Launcher

[ ] Integrate Cloud CAPTCHA APIs

[ ] Support CSV import/export

[ ] Docker support for deployment



---

📜 License

MIT License — free to use and modify for ethical automation only.


---

🤝 Contributing

Pull requests are welcome.
DM or fork it — let’s build something wild.


---

Built with ❤️ by @veerusjondy

---

Drop it in your `README.md` file at the root of your repo. You’re good to go. Need a badge set (stars, forks, license)? I can hook that up too.

