# Instagram_smm_panel
🔥 Fully automated Instagram bot that creates accounts, solves captchas, verifies with email/SMS, and performs actions like follow, like, and comment. Supports proxy rotation, headless mode, and one-click setup. Built for devs, testers, and bot researchers. Plug it in and let the matrix do the work.


Instagram Account Creation & Engagement Bot

Automated bot to generate and manage Instagram accounts, solve captchas, verify with email/SMS, and perform actions like follow/like/comment — all from one launch script.


---

🚀 Features

Account creation via browser automation (Playwright)

Captcha solving (CapMonster, AntiCaptcha ready)

Email verification (Mail.tm, 1secmail)

SMS activation (SMS-Activate)

Random user agents + proxy rotation

Auto proxy scraping from sslproxies.org

Post-registration actions (follow/like/comment)

Configurable via settings.yaml

Full logs & error tracking



---

🛠 Setup

1. Clone Repo

git clone https://github.com/veerusjondy/instagram_smm_panel.git

cd Instagram_smm_panel

2. Run One-Click Setup

python setup_launcher.py

That’s it. No manual file editing. Everything needed will auto-generate & run.


---

📁 Folder Structure

instagram_account_creator/
│
├── main.py                      # Account creation logic
├── launch_accounts_to_engage.py# Follow, Like, Comment engine
├── setup_launcher.py            # One-click installer & launcher
├── requirements.txt
├── README.md
│
├── config/
│   ├── proxies.txt
│   ├── user_agents.txt
│   ├── settings.yaml
│   └── targets.txt              # List of users to engage with
│
├── core/
│   ├── browser.py
│   ├── account_creator.py
│   ├── human_behavior.py
│   └── dashboard.py
│
├── utils/
│   ├── captcha_solver.py
│   ├── sms_handler.py
│   ├── email_verifier.py
│   ├── logger.py
│   ├── proxy_scraper.py
│   └── proxy_generator.py
│
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

MIT License — free to use and modify for ethical automation.


---

🤝 Contribute

PRs welcome! DM or fork and flex what you got.


---

Built with ❤️ by @veerusjondy
