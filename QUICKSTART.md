# Quick Setup Guide

## 🚀 Quick Start (5 minutes)

### 1. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure (Optional)
Edit `config.py` if you want to change:
- Password (default: `Outlook234!`)
- Browser settings
- Proxy settings

### 3. Run
```bash
python outlook_account_creator.py
```

### 4. Check Output
- Created accounts: `outlook_accounts.csv`
- Logs: `logs/` folder
- Screenshots (errors): `screenshots/` folder

## 📝 Example Output

```csv
Email,Password,First Name,Last Name
johnsmith1234@outlook.com,Outlook234!,John,Smith
sarahjohnson5678@outlook.com,Outlook234!,Sarah,Johnson
```

## 🔧 Optional: Using Proxies

1. Copy example file:
```bash
copy proxies.txt.example proxies.txt
```

2. Add your proxies to `proxies.txt`:
```
http://proxy1.example.com:8080
socks5://proxy2.example.com:1080
```

3. Enable in `config.py`:
```python
USE_PROXIES_FOR_OUTLOOK = True
```

## ⚡ Tips

- **First Run**: Use `HEADLESS_MODE = False` to watch the process
- **CAPTCHAs**: Solve manually when browser pauses
- **Rate Limits**: Increase `DELAY_BETWEEN_ACCOUNTS` if blocked
- **Debugging**: Check `logs/` and `screenshots/` folders

## 🆘 Common First-Time Issues

**Chrome version mismatch**
```bash
pip install --upgrade undetected-chromedriver
```

**Module not found**
```bash
pip install -r requirements.txt
```

**Permission denied (logs/screenshots)**
- Folders are auto-created, no action needed

## ✅ Success Checklist

- [ ] Python 3.8+ installed
- [ ] Chrome browser installed  
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Config reviewed (`config.py`)
- [ ] Script runs without errors

You're ready! 🎉
