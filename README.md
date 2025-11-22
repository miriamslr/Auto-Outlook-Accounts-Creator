# 🚀 Auto Outlook Accounts Creator

Automated Outlook/Hotmail account creator using Selenium and undetected-chromedriver. Bypass bot detection and create multiple accounts efficiently.

## This is Semi Automated, by which I mean is you need to solve captcha manually.

## Easy steps to solve the captcha:
- The current captcha system for account creation at outlook is, you need to press and hold for a few seconds and then it is solved
- But, in most of cases its glitchy, so the trick here is hold until it asks you to press and hold
- As soon as loading icons appear on the button, just move away faster and you will see a loading symbol in the form, if you see it, then you can release it
- If you dont see it or fail, try another 2-3 times until you are practiced
- Do it until you get, sometimes it might be IP issue if you aren't able to solve it, so change it before creating more
- Proxies mode is not tested, so use VPN on and proxies disabled, and everything will be good to go

## ✨ Features

- ✅ **Automated Account Creation**: Creates Outlook.com accounts with randomly generated names
- 🎭 **Bot Detection Bypass**: Uses undetected-chromedriver to avoid detection
- 🔄 **Proxy Support**: Optional proxy rotation for IP diversity
- 📊 **CSV Export**: Saves all created accounts to CSV file
- 🛡️ **Error Handling**: Robust error handling with retries and detailed logging
- 🖼️ **Screenshot Capture**: Automatic screenshots on errors for debugging
- ⚡ **Configurable**: Easy configuration via `config.py`

## 📋 Requirements

- Python 3.8+
- Chrome browser installed
- Windows/Linux/MacOS

## 🔧 Installation

### Option 1: Using Setup.exe (Easiest)

1. **Download Setup.exe** from [Releases](../../releases)
2. **Run it** - Double-click and follow prompts
3. It will auto-install Python dependencies and run the script

### Option 2: Manual (For Developers)

```bash
git clone https://github.com/akvanaparthy/Auto-Outlook-Accounts-Creator.git
cd Auto-Outlook-Accounts-Creator
pip install -r requirements.txt
python outlook_account_creator.py
```

## 🏗️ Building Setup.exe (Optional)

To create your own Setup.exe:
```bash
pip install pyinstaller
build_exe.bat
```
Find `Setup.exe` in `dist/` folder.

## ⚙️ Configuration

```python
# Password for all accounts
FIXED_PASSWORD = "Outlook234!"

# Browser settings
HEADLESS_MODE = False  # True = run in background
DISABLE_IMAGES = False  # True = faster but may affect CAPTCHAs

# Proxy settings
USE_PROXIES_FOR_OUTLOOK = False  # Enable proxy rotation
PROXY_FILE = "proxies.txt"
PROXY_TYPE = "http"  # or "socks5", "socks4"

# Account limits
TOTAL_ACCOUNTS = None  # None = unlimited, or set a number

# Timing
DELAY_BETWEEN_ACCOUNTS = 2  # Seconds between creations
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 15
```

## 🛠️ How It Works

1. **Name Generation**: Randomly generates first and last names from predefined lists
2. **Email Creation**: Combines name with random numbers (e.g., johnsmith1234@outlook.com)
3. **Browser Automation**: 
   - Launches undetected Chrome browser
   - Navigates to Outlook signup page
   - Fills in personal information
   - Handles password creation
   - Manages CAPTCHA challenges
   - Completes verification steps
4. **Data Storage**: Saves credentials to CSV in real-time

## 🐛 Troubleshooting

- **Chrome version mismatch**: `pip install --upgrade undetected-chromedriver`
- **Stuck on CAPTCHA**: Follow the manual steps mentioned at the top
- **Rate limited**: Use VPN, increase delays, switch IP

## ⚠️ Disclaimer

For educational purposes only. Comply with Microsoft's Terms of Service. Authors not responsible for misuse.
