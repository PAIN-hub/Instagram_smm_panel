# Instagram SMM Panel - Quick Setup & Execution Guide

This document provides complete instructions for configuring, initializing, and running the Instagram SMM Panel application.

---

## 1. System Requirements

- **Python**: Version 3.10, 3.11, 3.12, or 3.13.
- **Browser**: Google Chrome or Chromium (pre-installed on Linux/Windows/macOS or installed via Playwright).
- **SQLite3**: Bundled by default with Python.

---

## 2. Environment Setup

### Linux / macOS
```bash
# 1. Clone or navigate to the repository directory
cd Instagram_smm_panel

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate

# 4. Install python dependencies
pip install -r requirements.txt

# 5. (Optional) Install Playwright browser if Google Chrome is not installed system-wide
playwright install chromium
```

### Windows
```cmd
# 1. Open PowerShell or Command Prompt in the repository folder
cd Instagram_smm_panel

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate

# 4. Install python dependencies
pip install -r requirements.txt

# 5. (Optional) Install Playwright browser
playwright install chromium
```

---

## 3. Database Initialization

Run database migrations to generate and sync SQLite tables:

```bash
python manage.py makemigrations panel
python manage.py migrate
```

---

## 4. Running the Application

### A. Start the Web Dashboard
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your web browser.

### B. Start the Background Worker Daemon (Optional / Separate Terminal)
The web server includes an embedded task worker, but for dedicated high-throughput queue execution, you can run the standalone daemon in a second terminal:
```bash
# Ensure venv is activated
source venv/bin/activate

# Start queue worker
python manage.py run_worker
```

---

## 5. Configuration & Settings

Navigate to the **Settings** section on the web dashboard ([http://127.0.0.1:8000/settings/](http://127.0.0.1:8000/settings/)):

1. **Browser Engine**: Select **Chromium / Google Chrome (Recommended)**.
2. **Local Browser Path**: Leave empty for auto-detection (uses `/usr/bin/google-chrome` or system Chromium automatically).
3. **Headless Mode**:
   - `True` (Default): Runs browser invisibly in the background.
   - `False`: Opens visible browser window so you can watch automated registration or social interactions.
4. **Email Service**: Select **Mail.tm (Recommended)** for temporary email verification.
5. **CAPTCHA / SMS Providers**:
   - Add your CapMonster / AntiCaptcha API key.
   - Add your 5sim / SMS-Activate API key.

---

## 6. Proxy Health & Instagram Ping Checker

Navigate to the **Proxies** page ([http://127.0.0.1:8000/proxies/](http://127.0.0.1:8000/proxies/)):

- **Individual Ping**: Click the **Ping** button on any proxy row to send a handshake directly to Instagram through that proxy. The system measures real latency and categorizes the proxy health:
  - `Clean / Fast`: Responsive in under 2.5 seconds, HTTP 200, no challenge/block.
  - `Slow Response`: High latency (>= 2.5s).
  - `IG Blocked`: Instagram returned HTTP 429 (rate-limited), HTTP 403 (forbidden), or challenge intercept.
  - `Offline`: Connection timed out, proxy tunnel refused, or network unreachable.
- **Batch Verification**: Click **Ping & Verify All Proxies** to perform parallel health checks across your entire pool.
- **Smart Rotation**: The task queue worker automatically prioritizes verified `Clean / Fast` proxies and filters out `Blocked` or `Offline` IPs to prevent account burn.

---

## 7. Troubleshooting Common Issues

### Issue 1: "Stuck launching browser"
- **Cause**: Using stock system Firefox (`/usr/bin/firefox`) with Playwright. Playwright requires custom patched binaries or Chromium/Chrome DevTools Protocol.
- **Fix**: In **Settings**, ensure the browser is set to **Chromium / Google Chrome** and leave **Local Browser Path** empty.

### Issue 2: "Python was not found even if I had it installed" (Windows / Linux PATH)
- **Cause**: Python was not added to the system `PATH` during installation, or system PEP 668 restricts global pip installs.
- **Fix**:
  - On Windows: Re-run the Python installer and check **"Add Python to PATH"**.
  - On Linux: Always use `python3 -m venv venv` and `source venv/bin/activate`.

### Issue 3: "Failed to build wheel for greenlet / fatal error: Python.h"
- **Cause**: Older pinned `playwright==1.44.0` required compilation on Python 3.13+.
- **Fix**: The dependencies have been updated to `playwright>=1.48.0` which includes pre-compiled binary wheels.
