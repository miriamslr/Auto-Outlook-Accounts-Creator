# Configuration settings for Outlook Account Creator

# Outlook settings
OUTLOOK_ACCOUNTS_FILE = "outlook_accounts.csv"  # Created accounts stored here
OUTLOOK_IMAP_SERVER = "outlook.office365.com"
OUTLOOK_IMAP_PORT = 993

# Email domain
EMAIL_DOMAIN = "outlook.com"

# Password settings - FIXED PASSWORD FOR ALL ACCOUNTS
FIXED_PASSWORD = "Outlook234!"  # Default password for all accounts (change as needed)

# Proxy settings
PROXY_FILE = "proxies.txt"  # One proxy per line (http://ip:port or socks5://ip:port)
PROXY_TYPE = "http"  # Type: "http", "https", "socks4", or "socks5"
USE_PROXIES_FOR_OUTLOOK = False  # Set to True to use proxies (recommended: use VPN instead)

# Browser settings
HEADLESS_MODE = False  # Set to True to run browser in background
DISABLE_IMAGES = False  # Set to True to speed up (but may affect CAPTCHA detection)

# Timeout settings (in seconds)
PAGE_LOAD_TIMEOUT = 30
ELEMENT_WAIT_TIMEOUT = 15

# Output files
LOG_DIR = "logs"
SUCCESS_LOG_FILE = "logs/successful_accounts.log"
FAILED_LOG_FILE = "logs/failed_accounts.log"

# How many accounts to create (None = unlimited, or set a number)
TOTAL_ACCOUNTS = None

# Delay between account creations (in seconds)
DELAY_BETWEEN_ACCOUNTS = 2
