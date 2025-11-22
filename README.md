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

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd Auto-Outlook-Accounts-Creator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure settings:**
Edit `config.py` to customize:
- Password for accounts
- Proxy settings (optional)
- Browser settings (headless mode, etc.)
- Number of accounts to create

## 🚀 Usage

### Basic Usage

```bash
python outlook_account_creator.py
```

The script will:
1. Generate random first and last names
2. Create outlook.com email addresses
3. Navigate through Outlook signup process
4. Handle CAPTCHAs and verification steps
5. Save credentials to `outlook_accounts.csv`

### With Proxies (Optional)

1. Create `proxies.txt` with one proxy per line:
```
http://ip:port
http://username:password@ip:port
socks5://ip:port
```

2. Enable proxies in `config.py`:
```python
USE_PROXIES_FOR_OUTLOOK = True
PROXY_FILE = "proxies.txt"
```

## 📁 Output Files

### outlook_accounts.csv
Contains all successfully created accounts:
```csv
Email,Password,First Name,Last Name
johnsmith1234@outlook.com,Outlook234!,John,Smith
maryjones5678@outlook.com,Outlook234!,Mary,Jones
```

### logs/
- `successful_accounts.log` - Successful account creations
- `failed_accounts.log` - Failed attempts with error details

### screenshots/
- Automatic screenshots captured on errors
- Named with email prefix for easy debugging

## ⚙️ Configuration

### config.py Options

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

### Common Issues

**Issue**: "Chrome version mismatch"
```bash
# Solution: Update undetected-chromedriver
pip install --upgrade undetected-chromedriver
```

**Issue**: "Element not found" errors
- **Solution**: Website structure changed. May need selector updates in code
- Try running in non-headless mode to see what's happening

**Issue**: Stuck on CAPTCHA
- **Solution**: Manual intervention required
- Script will pause and wait for you to solve it
- Alternative: Use residential proxies to reduce CAPTCHA frequency

**Issue**: Account creation rate limited
- **Solution**: 
  - Increase `DELAY_BETWEEN_ACCOUNTS`
  - Use different proxies
  - Use VPN and switch locations

## 📊 Success Rate Tips

To improve success rate:
- ✅ Use residential proxies (better than datacenter)
- ✅ Add delays between attempts (2-5 seconds)
- ✅ Use VPN and rotate locations
- ✅ Run in non-headless mode initially to debug
- ✅ Check screenshots folder for error patterns
- ✅ Monitor logs for common failure points

## ⚠️ Important Notes

### Legal & Ethical Use
- This tool is for educational purposes and legitimate automation needs
- Ensure you comply with Microsoft's Terms of Service
- Do not use for spam, fraud, or malicious activities
- Respect rate limits and service guidelines
- Consider Microsoft's account creation policies

### Best Practices
- Don't create accounts too rapidly (use delays)
- Use proxies to distribute requests
- Keep success rate reasonable (not 100 accounts/hour)
- Store credentials securely
- Regularly update dependencies

### Limitations
- Microsoft may update signup flow (requires code updates)
- CAPTCHAs may require manual intervention
- IP-based rate limiting may occur
- Phone verification may be required (random)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is for educational purposes. Use responsibly and at your own risk.

## 🔗 Dependencies

- `undetected-chromedriver` - Bypass bot detection
- `selenium` - Browser automation
- `fake-useragent` - Randomize user agents

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review logs in `logs/` folder
3. Check screenshots in `screenshots/` folder
4. Open an issue with details

---

**⚠️ Disclaimer**: This tool is provided as-is for educational purposes. Users are responsible for complying with all applicable laws and terms of service. The authors assume no liability for misuse.
