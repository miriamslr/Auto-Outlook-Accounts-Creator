#!/usr/bin/env python3
"""
Outlook Account Creator
Automates creation of Outlook/Hotmail email accounts
"""

import time
import random
import string
import logging
import csv
from typing import Dict, Optional, List
from datetime import datetime
from faker import Faker
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import config


class OutlookAccountCreator:
    """Creates Outlook/Hotmail email accounts"""

    SIGNUP_URL = "https://signup.live.com"

    def __init__(self, proxy: Optional[str] = None, headless: bool = True, locale: Optional[str] = None):
        """
        Initialize Outlook account creator

        Args:
            proxy: Proxy to use for browser (format: ip:port)
            headless: Run browser in headless mode
            locale: Faker locale (e.g., 'en_US', 'pt_BR', 'es_ES'). 
                    If None, uses FAKER_LOCALE from config.py
        """
        # Use locale from parameter, config, or default to 'pt_BR'
        faker_locale = locale or getattr(config, 'FAKER_LOCALE', 'pt_BR')
        self.faker = Faker(faker_locale)
        self.proxy = proxy
        self.headless = headless
        logging.info(f"Faker initialized with locale: {faker_locale}")
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _create_browser(self) -> uc.Chrome:
        """Create undetected Chrome browser instance with proxy support"""
        options = uc.ChromeOptions()

        # Performance optimizations
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Suppress errors and warnings
        options.add_argument('--log-level=3')

        # Additional stealth options to avoid detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')

        # Set realistic user preferences (compatible with all Chrome versions)
        try:
            prefs = {
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False,
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
        except:
            pass  # Older Chrome versions may not support this

        # Proxy configuration
        use_proxies = getattr(config, 'USE_PROXIES_FOR_OUTLOOK', True)
        if self.proxy and use_proxies:
            proxy_type = getattr(config, 'PROXY_TYPE', 'socks5')
            options.add_argument(f'--proxy-server={proxy_type}://{self.proxy}')
            logging.info(f"Using {proxy_type.upper()} proxy: {self.proxy}")
        else:
            if not use_proxies:
                logging.info("Proxies disabled for Outlook account creation")
            else:
                logging.warning("No proxy configured for account creation")

        # Create undetected Chrome driver (bypasses automation detection)
        # undetected_chromedriver handles anti-detection automatically
        driver = uc.Chrome(
            options=options,
            headless=self.headless,
            use_subprocess=False
        )

        # Inject additional stealth JavaScript to hide automation
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                window.chrome = {
                    runtime: {}
                };
            '''
        })

        driver.set_page_load_timeout(config.PAGE_LOAD_TIMEOUT)
        return driver

    def generate_username(self) -> str:
        """Generate a random username for Outlook"""
        # Use faker for realistic names
        first = self.faker.first_name().lower()
        last = self.faker.last_name().lower()

        # Add random numbers for uniqueness
        random_num = ''.join(random.choices(string.digits, k=4))

        # Format: firstnamelastname1234
        username = f"{first}{last}{random_num}"

        return username

    def generate_password(self) -> str:
        """Generate password (returns fixed password from config)"""
        return config.FIXED_PASSWORD

    def create_account(self, proxy: Optional[str] = None) -> Optional[Dict]:
        """
        Create a new Outlook account

        Args:
            proxy: Proxy to use for this request (overrides instance proxy)

        Returns:
            Dict with keys: email, password, first_name, last_name
            None if creation failed
        """
        # Update proxy if provided
        if proxy:
            self.proxy = proxy

        driver = None
        try:
            # Generate account details - generate name first, then use it for email
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            
            # Generate second last name (4 letters) for email uniqueness
            second_last_name = self.faker.last_name().lower()
            # Take first 4 letters, or pad if shorter
            second_last_4 = (second_last_name[:4] if len(second_last_name) >= 4 
                            else second_last_name + 'x' * (4 - len(second_last_name)))[:4]
            
            # Generate username from the same name (lowercase, no spaces, with second last name)
            first_lower = first_name.lower()
            last_lower = last_name.lower()
            username = f"{first_lower}{last_lower}{second_last_4}"
            
            password = self.generate_password()

            # Random birth date (age 18-50)
            birth_year = random.randint(1974, 2006)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)

            # Full email address with domain
            email = f"{username}@outlook.com"

            logging.info(f"Creating Outlook account: {email}")
            logging.info(f"Name: {first_name} {last_name}")

            # Create browser
            driver = self._create_browser()

            # Navigate to signup page
            logging.info("Loading Outlook signup page...")
            driver.get(self.SIGNUP_URL)

            wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
            wait_short = WebDriverWait(driver, 3)  # Shorter wait for trying multiple selectors

            # STEP 1: Enter email/username
            logging.info("Step 1: Entering email/username...")

            # Take screenshot of initial page
            self._take_screenshot(driver, "step1_initial_page")
            logging.info(f"Current URL: {driver.current_url}")

            try:
                # Try multiple selectors for username input
                username_input = None
                selectors = [
                    (By.NAME, "MemberName"),
                    (By.ID, "MemberName"),
                    (By.CSS_SELECTOR, "input[type='email']"),
                    (By.CSS_SELECTOR, "input[name='MemberName']"),
                    (By.XPATH, "//input[@type='email']")
                ]

                for selector_type, selector_value in selectors:
                    try:
                        username_input = wait_short.until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        logging.info(f"✓ Found username input with: {selector_type} = {selector_value}")
                        break
                    except:
                        continue

                if not username_input:
                    logging.error("Could not find username input field with any selector")
                    self._take_screenshot(driver, "error_no_username_field")
                    return None

                # Try up to 3 different emails if username is taken
                max_email_attempts = 3
                email_accepted = False
                
                for attempt in range(max_email_attempts):
                    if attempt > 0:
                        # Generate new email for retry - keep same name, just change second last name
                        second_last_name = self.faker.last_name().lower()
                        second_last_4 = (second_last_name[:4] if len(second_last_name) >= 4 
                                        else second_last_name + 'x' * (4 - len(second_last_name)))[:4]
                        first_lower = first_name.lower()
                        last_lower = last_name.lower()
                        username = f"{first_lower}{last_lower}{second_last_4}"
                        email = f"{username}@outlook.com"
                        logging.info(f"Attempt {attempt + 1}: Trying new email: {email}")
                    
                    username_input.clear()
                    username_input.send_keys(email)
                    logging.info(f"✓ Entered email: {email}")
                    time.sleep(1)  # Wait for validation

                    # Check for "username already taken" error
                    try:
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        if "already taken" in page_text.lower() or "try another" in page_text.lower():
                            logging.warning(f"⚠ Email {email} is already taken!")
                            self._take_screenshot(driver, f"email_taken_attempt{attempt+1}")
                            
                            if attempt < max_email_attempts - 1:
                                logging.info("Will try with a different email...")
                                continue
                            else:
                                logging.error(f"Failed after {max_email_attempts} email attempts")
                                return None
                        else:
                            # No error detected - email accepted
                            email_accepted = True
                            break
                    except:
                        # If we can't check for errors, assume email is accepted
                        email_accepted = True
                        break

                if not email_accepted:
                    logging.error("Could not find available email username")
                    return None

                time.sleep(0.2)  # Reduced from 0.5s

                # Click Next button using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after email"):
                    logging.error("Could not find Next button with any selector")
                    self._take_screenshot(driver, "error_next_button")
                    return None
                
                time.sleep(1)  # Wait for page to load
                
                # After clicking Next, check again for email error
                time.sleep(1)
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    current_url = driver.current_url
                    
                    if "signup.live.com" in current_url and "MemberName" in current_url:
                        if "already taken" in page_text.lower():
                            logging.error("Email was rejected after clicking Next")
                            self._take_screenshot(driver, "email_rejected_after_next")
                            return None
                except:
                    pass

            except Exception as e:
                logging.error(f"Failed at step 1 (username): {e}")
                self._take_screenshot(driver, "error_step1")
                logging.error(f"Page source length: {len(driver.page_source)}")
                return None

            # STEP 2: Enter password
            logging.info("Step 2: Entering password...")
            self._take_screenshot(driver, "step2_password_page")

            try:
                # Try multiple selectors for password input
                password_input = None
                password_selectors = [
                    (By.NAME, "Password"),
                    (By.ID, "Password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.CSS_SELECTOR, "input[name='Password']"),
                    (By.XPATH, "//input[@type='password']")
                ]

                for selector_type, selector_value in password_selectors:
                    try:
                        password_input = wait_short.until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        logging.info(f"✓ Found password input with: {selector_type} = {selector_value}")
                        break
                    except:
                        continue

                if not password_input:
                    logging.error("Could not find password input field with any selector")
                    self._take_screenshot(driver, "error_no_password_field")
                    return None

                password_input.clear()
                password_input.send_keys(password)
                logging.info(f"✓ Entered password")
                time.sleep(0.5)  # Wait for password validation

                # Click Next button using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after password"):
                    logging.error("Could not find Next button after password")
                    self._take_screenshot(driver, "error_next_button_step2")
                    return None
                
                time.sleep(1)  # Wait for next page to load

            except Exception as e:
                logging.error(f"Failed at step 2 (password): {e}")
                self._take_screenshot(driver, "error_step2")
                return None

            # STEP 3: Enter Country and DOB (this comes before name!)
            logging.info("Step 3: Entering Country and DOB...")
            time.sleep(0.5)  # Reduced from 1s
            self._take_screenshot(driver, "step3_country_dob_page")

            try:
                logging.info(f"Current URL: {driver.current_url}")
                logging.info(f"Page title: {driver.title}")

                # Print visible text on page (first 500 chars) for debugging
                try:
                    body_text = driver.find_element(By.TAG_NAME, "body").text
                    logging.info(f"Page text preview: {body_text[:500]}")
                except:
                    pass

                # Try to find and select Country dropdown (optional)
                country_found = False
                country_selectors = [
                    (By.ID, "Country"),
                    (By.NAME, "Country"),
                    (By.CSS_SELECTOR, "select[name='Country']")
                ]

                for selector_type, selector_value in country_selectors:
                    try:
                        country_select = Select(driver.find_element(selector_type, selector_value))
                        country_select.select_by_value("US")
                        logging.info("✓ Selected country: US")
                        country_found = True
                        break
                    except:
                        continue

                if not country_found:
                    logging.info("No country field found (may not be required)")

                # Enter birth date - Using improved selectors based on TypeScript reference
                dob_entered = False

                # Wait for DOB fields to load
                try:
                    logging.info("Waiting for DOB fields to load...")
                    time.sleep(1.5)  # Give page time to fully render

                    # DAY - Improved selectors (Portuguese and English, with IDs)
                    day_selectors = [
                        (By.ID, "BirthDayDropdown"),
                        (By.CSS_SELECTOR, "select[id='BirthDayDropdown']"),
                        (By.CSS_SELECTOR, "combobox[id='BirthDayDropdown']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Day' i]"),
                        (By.NAME, "BirthDay"),
                        (By.CSS_SELECTOR, "select[name='BirthDay']"),
                        (By.CSS_SELECTOR, "select[id='BirthDay']"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "div[aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Day' i]"),
                    ]

                    day_element = None
                    found_day_selector = None
                    for selector_type, selector_value in day_selectors:
                        try:
                            day_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            found_day_selector = (selector_type, selector_value)
                            logging.info(f"✓ Found day field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not day_element:
                        logging.error("Could not find day field with any selector")
                        self._take_screenshot(driver, "error_day_field_not_found")
                        raise Exception("Could not find Day field")

                    # Check if it's a select or combobox
                    tag_name = day_element.tag_name.lower()
                    day_selected = False

                    if tag_name == 'select':
                        # HTML select - use Select class
                        logging.info("Day field is HTML select, using Select class")
                        try:
                            select = Select(day_element)
                            select.select_by_value(str(birth_day))
                            day_selected = True
                            logging.info(f"✓ Selected day {birth_day} via Select")
                        except:
                            try:
                                select.select_by_visible_text(str(birth_day))
                                day_selected = True
                                logging.info(f"✓ Selected day {birth_day} via visible text")
                            except Exception as e:
                                logging.error(f"Error selecting day via Select: {e}")
                    else:
                        # Custom combobox - click and select option
                        logging.info("Day field is custom combobox, clicking and selecting option")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", day_element)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", day_element)
                        time.sleep(0.5)

                        # Try to find and click the day option
                        day_value = str(birth_day)
                        day_option_selectors = [
                            (By.XPATH, f"//*[@role='option'][@aria-label='{day_value}']"),
                            (By.XPATH, f"//*[@role='option'][text()='{day_value}']"),
                            (By.XPATH, f"//option[@value='{day_value}']"),
                            (By.XPATH, f"//li[text()='{day_value}']"),
                            (By.XPATH, f"//div[text()='{day_value}']"),
                            (By.XPATH, f"//*[text()='{day_value}']"),
                        ]

                        for opt_type, opt_value in day_option_selectors:
                            try:
                                day_option = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((opt_type, opt_value))
                                )
                                day_option.click()
                                day_selected = True
                                logging.info(f"✓ Selected day {day_value}")
                                break
                            except:
                                continue

                        # Fallback: JavaScript search
                        if not day_selected:
                            logging.warn("Trying JavaScript fallback for day selection")
                            clicked = driver.execute_script("""
                                const options = Array.from(document.querySelectorAll('[role="option"], option, li, div'));
                                const dayOption = options.find(opt => {
                                    const text = opt.textContent?.trim();
                                    const ariaLabel = opt.getAttribute('aria-label');
                                    return text === arguments[0] || ariaLabel === arguments[0];
                                });
                                if (dayOption) {
                                    dayOption.click();
                                    return true;
                                }
                                return false;
                            """, day_value)
                            if clicked:
                                day_selected = True
                                logging.info(f"✓ Selected day {day_value} via JavaScript")

                    if not day_selected:
                        raise Exception(f"Could not select day {birth_day}")

                    time.sleep(0.3)

                    # MONTH - Improved selectors with Portuguese month names
                    month_selectors = [
                        (By.ID, "BirthMonthDropdown"),
                        (By.CSS_SELECTOR, "select[id='BirthMonthDropdown']"),
                        (By.CSS_SELECTOR, "combobox[id='BirthMonthDropdown']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Month' i]"),
                        (By.NAME, "BirthMonth"),
                        (By.CSS_SELECTOR, "select[name='BirthMonth']"),
                        (By.CSS_SELECTOR, "select[id='BirthMonth']"),
                        (By.CSS_SELECTOR, "button[aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "div[aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Month' i]"),
                    ]

                    month_names_pt = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                                      'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                    month_names_en = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                                     'July', 'August', 'September', 'October', 'November', 'December']
                    
                    month_name_pt = month_names_pt[birth_month]
                    month_name_en = month_names_en[birth_month]
                    month_num = str(birth_month)

                    month_element = None
                    for selector_type, selector_value in month_selectors:
                        try:
                            month_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            logging.info(f"✓ Found month field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not month_element:
                        raise Exception("Could not find Month field")

                    tag_name = month_element.tag_name.lower()
                    month_selected = False

                    if tag_name == 'select':
                        # HTML select
                        logging.info("Month field is HTML select")
                        try:
                            select = Select(month_element)
                            select.select_by_value(month_num)
                            month_selected = True
                            logging.info(f"✓ Selected month {month_num} via Select")
                        except:
                            try:
                                select.select_by_visible_text(month_name_pt)
                                month_selected = True
                                logging.info(f"✓ Selected month {month_name_pt} via Select")
                            except:
                                try:
                                    select.select_by_visible_text(month_name_en)
                                    month_selected = True
                                    logging.info(f"✓ Selected month {month_name_en} via Select")
                                except Exception as e:
                                    logging.error(f"Error selecting month via Select: {e}")
                    else:
                        # Custom combobox
                        logging.info("Month field is custom combobox")
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", month_element)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", month_element)
                        time.sleep(0.5)

                        # Try Portuguese first, then English, then number
                        month_option_selectors = [
                            (By.XPATH, f"//*[@role='option'][contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//*[@role='option'][contains(text(), '{month_name_en}')]"),
                            (By.XPATH, f"//*[@role='option'][text()='{month_num}']"),
                            (By.XPATH, f"//*[contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//*[contains(text(), '{month_name_en}')]"),
                            (By.XPATH, f"//li[contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//div[contains(text(), '{month_name_pt}')]"),
                        ]

                        for opt_type, opt_value in month_option_selectors:
                            try:
                                month_option = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((opt_type, opt_value))
                                )
                                month_option.click()
                                month_selected = True
                                logging.info(f"✓ Selected month {month_name_pt}")
                                break
                            except:
                                continue

                        # JavaScript fallback
                        if not month_selected:
                            clicked = driver.execute_script("""
                                const options = Array.from(document.querySelectorAll('[role="option"], option, li, div'));
                                const monthOption = options.find(opt => {
                                    const text = opt.textContent?.toLowerCase().trim();
                                    return text.includes(arguments[0].toLowerCase()) || text === arguments[1];
                                });
                                if (monthOption) {
                                    monthOption.click();
                                    return true;
                                }
                                return false;
                            """, month_name_pt, month_num)
                            if clicked:
                                month_selected = True
                                logging.info(f"✓ Selected month via JavaScript")

                    if not month_selected:
                        raise Exception(f"Could not select month {birth_month}")

                    time.sleep(0.3)

                    # YEAR - Improved selectors
                    year_selectors = [
                        (By.NAME, "BirthYear"),
                        (By.ID, "BirthYear"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Year' i]"),
                        (By.CSS_SELECTOR, "select[name='BirthYear']"),
                        (By.CSS_SELECTOR, "select[id='BirthYear']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[aria-label*='Year' i]"),
                    ]

                    year_element = None
                    for selector_type, selector_value in year_selectors:
                        try:
                            year_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            logging.info(f"✓ Found year field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not year_element:
                        raise Exception("Could not find Year field")

                    tag_name = year_element.tag_name.lower()
                    year_filled = False

                    if tag_name == 'select':
                        # HTML select
                        select = Select(year_element)
                        select.select_by_value(str(birth_year))
                        year_filled = True
                        logging.info(f"✓ Selected year {birth_year} via Select")
                    else:
                        # Input field
                        year_element.clear()
                        year_element.send_keys(str(birth_year))
                        year_filled = True
                        logging.info(f"✓ Entered year {birth_year}")

                    if not year_filled:
                        raise Exception(f"Could not fill year {birth_year}")

                    dob_entered = True
                    logging.info(f"✓ Successfully entered complete DOB: {birth_day}/{birth_month}/{birth_year}")

                except TimeoutException:
                    logging.error("Timeout waiting for DOB fields")
                    self._take_screenshot(driver, "timeout_dob_fields")
                except Exception as e:
                    logging.error(f"Error entering DOB: {e}")
                    self._take_screenshot(driver, "error_dob_entry")

                    # Debug: Print all button and input elements
                    try:
                        all_buttons = driver.find_elements(By.TAG_NAME, "button")
                        all_inputs = driver.find_elements(By.TAG_NAME, "input")
                        all_divs = driver.find_elements(By.CSS_SELECTOR, "div[role='combobox']")

                        logging.info(f"DEBUG: Found {len(all_buttons)} buttons, {len(all_inputs)} inputs, {len(all_divs)} combobox divs")

                        for i, btn in enumerate(all_buttons[:5]):
                            btn_attrs = {
                                'text': btn.text[:30] if btn.text else 'no-text',
                                'aria-label': btn.get_attribute("aria-label"),
                                'class': btn.get_attribute("class")[:50] if btn.get_attribute("class") else 'no-class'
                            }
                            logging.info(f"  Button #{i+1}: {btn_attrs}")

                        for i, inp in enumerate(all_inputs[:5]):
                            inp_attrs = {
                                'name': inp.get_attribute("name"),
                                'type': inp.get_attribute("type"),
                                'aria-label': inp.get_attribute("aria-label"),
                                'placeholder': inp.get_attribute("placeholder")
                            }
                            logging.info(f"  Input #{i+1}: {inp_attrs}")
                    except:
                        pass

                if not dob_entered:
                    logging.error("CRITICAL: Could not enter DOB - cannot continue")
                    self._take_screenshot(driver, "failed_dob")
                    return None

                time.sleep(0.5)  # Reduced from 1s - Give page time to be ready for Next button

                # Click Next button after DOB using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after country/DOB"):
                    logging.warning("Could not auto-click Next button - may already be on next page or needs manual click")
                
                time.sleep(1)  # Wait for page to navigate

            except Exception as e:
                logging.error(f"Failed at step 3 (country/DOB): {e}")
                self._take_screenshot(driver, "error_step3")
                # Don't return None - continue to next step

            # STEP 4: Enter name (comes AFTER country/DOB) - OR MAYBE IT'S CAPTCHA?
            logging.info("Step 4: Checking for name fields or CAPTCHA...")
            time.sleep(0.5)  # Reduced from 1s
            self._take_screenshot(driver, "step4_name_page")
            logging.info(f"Current URL: {driver.current_url}")

            try:
                # Try to find first name with multiple selectors
                first_name_found = False
                first_name_selectors = [
                    (By.CSS_SELECTOR, "input[aria-label*='First' i]"),
                    (By.NAME, "FirstName"),
                    (By.ID, "FirstName"),
                    (By.CSS_SELECTOR, "input[name='FirstName']"),
                    (By.CSS_SELECTOR, "input[type='text']:first-of-type"),
                    (By.XPATH, "//label[contains(text(), 'First')]/following-sibling::input"),
                    (By.XPATH, "//input[contains(@placeholder, 'First')]"),
                    (By.XPATH, "//input[@type='text'][1]"),
                ]

                first_name_input = None
                for selector_type, selector_value in first_name_selectors:
                    try:
                        first_name_input = wait_short.until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        first_name_input.clear()
                        first_name_input.send_keys(first_name)
                        logging.info(f"✓ Entered first name: {first_name}")
                        first_name_found = True
                        time.sleep(0.5)  # Let page stabilize after first name entry
                        break
                    except:
                        continue

                if not first_name_found:
                    logging.info("No first name field found - might be at CAPTCHA or different page")
                    # Check if we're at CAPTCHA page
                    try:
                        captcha = driver.find_element(By.ID, "enforcementFrame")
                        logging.info("Found CAPTCHA - skipping name step")
                    except:
                        logging.warning("No name fields and no CAPTCHA found")
                        self._take_screenshot(driver, "unknown_page_step4")
                else:
                    # Try to find and fill last name (simpler approach: get all text inputs, take 2nd one)
                    time.sleep(0.3)  # Brief pause for page to be ready
                    # Simple approach: Find all text inputs on page, second one should be last name
                    last_name_found = False
                    try:
                        # Wait for text inputs to be present
                        wait_short.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "input[type='text']")))

                        # Get all text inputs
                        text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")

                        if len(text_inputs) >= 2:
                            # Second input should be last name
                            last_name_input = text_inputs[1]
                            last_name_input.clear()
                            last_name_input.send_keys(last_name)
                            logging.info(f"✓ Entered last name: {last_name} (using 2nd text input)")
                            last_name_found = True
                        else:
                            logging.warning(f"Found only {len(text_inputs)} text input(s), expected at least 2")
                    except Exception as e:
                        logging.warning(f"Could not find last name field: {e}")

                    if not last_name_found:
                        logging.warning("Trying alternative last name selectors...")
                        # Fallback selectors
                        last_name_selectors = [
                            (By.CSS_SELECTOR, "input[aria-label*='Last' i]"),
                            (By.NAME, "LastName"),
                            (By.XPATH, "//label[contains(text(), 'Last')]/following-sibling::input"),
                        ]

                        for selector_type, selector_value in last_name_selectors:
                            try:
                                last_name_input = driver.find_element(selector_type, selector_value)
                                last_name_input.clear()
                                last_name_input.send_keys(last_name)
                                logging.info(f"✓ Entered last name: {last_name}")
                                last_name_found = True
                                break
                            except:
                                continue

                    time.sleep(0.5)

                    # Click Next button after name using helper method (supports Portuguese and English)
                    if not self._click_next_button(driver, wait_time=5, context="after name"):
                        logging.warning("Could not click Next button after name")
                    
                    time.sleep(1)

            except Exception as e:
                logging.warning(f"Issue at step 4 (name): {e}")
                self._take_screenshot(driver, "error_step4")
                # Don't return None - continue to CAPTCHA check

            # STEP 5: Handle CAPTCHA
            logging.info("Step 5: Checking for CAPTCHA...")
            time.sleep(1)  # Reduced from 1.5s
            self._take_screenshot(driver, "step5_captcha_check")

            # Check for CAPTCHA (multiple detection methods)
            captcha_detected = False
            try:
                # Method 1: Look for "Let's prove you're human" text
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "prove you're human" in page_text.lower() or "let's prove" in page_text.lower():
                    captcha_detected = True
                    logging.warning("⚠ CAPTCHA detected (modern interactive CAPTCHA)!")

                # Method 2: Look for enforcementFrame
                elif driver.find_elements(By.ID, "enforcementFrame"):
                    captcha_detected = True
                    logging.warning("⚠ CAPTCHA detected (enforcement frame)!")

                # Method 3: Check for CAPTCHA-related elements
                elif driver.find_elements(By.CSS_SELECTOR, "[aria-label*='verification' i]") or \
                     driver.find_elements(By.CSS_SELECTOR, "[aria-label*='captcha' i]"):
                    captcha_detected = True
                    logging.warning("⚠ CAPTCHA detected (verification element)!")

            except:
                pass

            if captcha_detected:
                logging.warning("=" * 60)
                logging.warning("MANUAL CAPTCHA SOLVING REQUIRED")
                logging.warning("Please solve the CAPTCHA in the browser window")
                logging.warning("Waiting up to 3 minutes for you to complete it...")
                logging.warning("=" * 60)

                # Wait up to 3 minutes for CAPTCHA to be solved
                max_wait = 180  # 3 minutes
                start_time = time.time()

                while (time.time() - start_time) < max_wait:
                    time.sleep(2)

                    # Check if we've moved past the CAPTCHA page
                    try:
                        current_url = driver.current_url
                        page_text = driver.find_element(By.TAG_NAME, "body").text

                        # If we're no longer on CAPTCHA page, break
                        if "prove you're human" not in page_text.lower() and \
                           "let's prove" not in page_text.lower():
                            logging.info("✓ CAPTCHA appears to be solved! Continuing...")
                            time.sleep(2)  # Give page time to fully load

                            # Now click the Next button after CAPTCHA using helper method
                            logging.info("Looking for Next button after CAPTCHA...")
                            if self._click_next_button(driver, wait_time=5, context="after CAPTCHA"):
                                time.sleep(3)  # Wait for navigation
                            else:
                                logging.warning("Could not find Next button after CAPTCHA - may auto-proceed")
                                time.sleep(3)

                            break
                    except:
                        pass
                else:
                    logging.error("CAPTCHA not solved within 3 minute timeout")
                    self._take_screenshot(driver, "captcha_timeout")
                    return None
            else:
                logging.info("No CAPTCHA detected, continuing...")

            # STEP 6: Verify account creation success
            logging.info("Verifying account creation...")
            time.sleep(1)  # Reduced from 1.5s - Give page time to settle
            self._take_screenshot(driver, "final_page")

            # Check if we're at the success page or inbox
            current_url = driver.current_url
            logging.info(f"Final URL: {current_url}")

            # Success indicators
            success_indicators = [
                "outlook.live.com",
                "account.microsoft.com",
                "signup.live.com/proofs",
                "/signup?wa=wsignin"
            ]

            is_success = any(indicator in current_url for indicator in success_indicators)

            if is_success:
                logging.info(f"✓ Account created successfully: {email}")

                return {
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Check if still at signup - might need manual intervention
                if "signup.live.com" in current_url:
                    logging.warning("Still at signup page - check if manual steps needed")
                    logging.warning("Waiting 30 seconds for manual intervention...")
                    time.sleep(30)

                    # Check again
                    current_url = driver.current_url
                    logging.info(f"URL after wait: {current_url}")

                    if any(indicator in current_url for indicator in success_indicators):
                        logging.info(f"✓ Account created successfully after manual intervention: {email}")
                        return {
                            'email': email,
                            'password': password,
                            'first_name': first_name,
                            'last_name': last_name,
                            'birth_date': f"{birth_year}-{birth_month:02d}-{birth_day:02d}",
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }

                logging.error(f"Account creation unclear. Current URL: {current_url}")
                self._take_screenshot(driver, "error_final")
                return None

        except Exception as e:
            logging.error(f"Exception creating Outlook account: {e}")
            if driver:
                self._take_screenshot(driver, "error_exception")
            return None

        finally:
            if driver:
                driver.quit()

    def create_account_keep_open(self, proxy: Optional[str] = None) -> Optional[Dict]:
        """
        Create a new Outlook account and return BOTH account data AND driver
        DOES NOT close browser - returns driver for continued use

        Args:
            proxy: Proxy to use for this request (overrides instance proxy)

        Returns:
            Dict with keys: driver, email, password, first_name, last_name, birth_date
            None if creation failed

        IMPORTANT: Caller is responsible for closing the driver when done!
        """
        # Update proxy if provided
        if proxy:
            self.proxy = proxy

        driver = None

        try:
            # Generate account details - generate name first, then use it for email (EXACT same as create_account method)
            first_name = self.faker.first_name()
            last_name = self.faker.last_name()
            
            # Generate second last name (4 letters) for email uniqueness
            second_last_name = self.faker.last_name().lower()
            # Take first 4 letters, or pad if shorter
            second_last_4 = (second_last_name[:4] if len(second_last_name) >= 4 
                            else second_last_name + 'x' * (4 - len(second_last_name)))[:4]
            
            # Generate username from the same name (lowercase, no spaces, with second last name)
            first_lower = first_name.lower()
            last_lower = last_name.lower()
            username = f"{first_lower}{last_lower}{second_last_4}"
            
            password = self.generate_password()

            # Random birth date (age 18-50)
            birth_year = random.randint(1974, 2006)
            birth_month = random.randint(1, 12)
            birth_day = random.randint(1, 28)
            birth_date = f"{birth_year}-{birth_month:02d}-{birth_day:02d}"

            # Full email address with domain
            email = f"{username}@outlook.com"

            logging.info(f"Creating Outlook account: {email}")
            logging.info(f"Name: {first_name} {last_name}")

            # Create browser
            driver = self._create_browser()

            # Navigate to signup page
            logging.info("Loading Outlook signup page...")
            driver.get(self.SIGNUP_URL)

            wait = WebDriverWait(driver, config.ELEMENT_WAIT_TIMEOUT)
            wait_short = WebDriverWait(driver, 3)

            # STEP 1: Enter email/username (SAME logic as create_account)
            logging.info("Step 1: Entering email/username...")
            self._take_screenshot(driver, "keepopen_step1_initial_page")
            logging.info(f"Current URL: {driver.current_url}")

            try:
                # Try multiple selectors for username input
                username_input = None
                selectors = [
                    (By.NAME, "MemberName"),
                    (By.ID, "MemberName"),
                    (By.CSS_SELECTOR, "input[type='email']"),
                    (By.CSS_SELECTOR, "input[name='MemberName']"),
                    (By.XPATH, "//input[@type='email']")
                ]

                for selector_type, selector_value in selectors:
                    try:
                        username_input = wait_short.until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        logging.info(f"✓ Found username input with: {selector_type} = {selector_value}")
                        break
                    except:
                        continue

                if not username_input:
                    logging.error("Could not find username input field")
                    self._take_screenshot(driver, "keepopen_error_no_username_field")
                    return {'driver': driver, 'error': 'No username field found'}

                # Try up to 3 different emails if username is taken
                max_email_attempts = 3
                email_accepted = False
                
                for attempt in range(max_email_attempts):
                    if attempt > 0:
                        # Generate new email for retry - keep same name, just change second last name
                        second_last_name = self.faker.last_name().lower()
                        second_last_4 = (second_last_name[:4] if len(second_last_name) >= 4 
                                        else second_last_name + 'x' * (4 - len(second_last_name)))[:4]
                        first_lower = first_name.lower()
                        last_lower = last_name.lower()
                        username = f"{first_lower}{last_lower}{second_last_4}"
                        email = f"{username}@outlook.com"
                        logging.info(f"Attempt {attempt + 1}: Trying new email: {email}")
                    
                    username_input.clear()
                    username_input.send_keys(email)
                    logging.info(f"✓ Entered email: {email}")
                    time.sleep(1)  # Wait for validation

                    # Check for "username already taken" error
                    try:
                        page_text = driver.find_element(By.TAG_NAME, "body").text
                        if "already taken" in page_text.lower() or "try another" in page_text.lower():
                            logging.warning(f"⚠ Email {email} is already taken!")
                            self._take_screenshot(driver, f"keepopen_email_taken_attempt{attempt+1}")
                            
                            # Check for error message elements
                            error_elements = driver.find_elements(By.CSS_SELECTOR, "[role='alert']")
                            error_elements += driver.find_elements(By.CSS_SELECTOR, ".alert-error")
                            error_elements += driver.find_elements(By.CSS_SELECTOR, "[aria-live='polite']")
                            
                            for elem in error_elements:
                                if "taken" in elem.text.lower():
                                    logging.warning(f"Error message: {elem.text}")
                            
                            if attempt < max_email_attempts - 1:
                                logging.info("Will try with a different email...")
                                continue
                            else:
                                logging.error(f"Failed after {max_email_attempts} email attempts")
                                return {'driver': driver, 'error': 'All email attempts taken'}
                        else:
                            # No error detected - email accepted
                            email_accepted = True
                            break
                    except:
                        # If we can't check for errors, assume email is accepted
                        email_accepted = True
                        break

                if not email_accepted:
                    logging.error("Could not find available email username")
                    return {'driver': driver, 'error': 'Email validation failed'}

                time.sleep(0.5)

                # Click Next button using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after email"):
                    logging.error("Could not find Next button")
                    self._take_screenshot(driver, "keepopen_error_next_button")
                    return {'driver': driver, 'error': 'No Next button found'}
                
                time.sleep(1.5)  # Wait for page to load
                
                # After clicking Next, check again for email error (in case it appears after click)
                time.sleep(1)
                try:
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    current_url = driver.current_url
                    
                    # If still on email page with error, email was rejected
                    if "signup.live.com" in current_url and "MemberName" in current_url:
                        if "already taken" in page_text.lower():
                            logging.error("Email was rejected after clicking Next")
                            self._take_screenshot(driver, "keepopen_email_rejected_after_next")
                            return {'driver': driver, 'error': 'Email rejected'}
                except:
                    pass

            except Exception as e:
                logging.error(f"Failed at step 1 (username): {e}")
                self._take_screenshot(driver, "keepopen_error_step1")
                return {'driver': driver, 'error': str(e)}

            # STEP 2: Enter password (SAME logic as create_account)
            logging.info("Step 2: Entering password...")
            self._take_screenshot(driver, "keepopen_step2_password_page")

            try:
                password_input = None
                password_selectors = [
                    (By.NAME, "Password"),
                    (By.ID, "Password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.CSS_SELECTOR, "input[name='Password']"),
                    (By.XPATH, "//input[@type='password']")
                ]

                for selector_type, selector_value in password_selectors:
                    try:
                        password_input = wait_short.until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        logging.info(f"✓ Found password input")
                        break
                    except:
                        continue

                if not password_input:
                    logging.error("Could not find password input field")
                    self._take_screenshot(driver, "keepopen_error_no_password_field")
                    return {'driver': driver, 'error': 'No password field found'}

                password_input.clear()
                password_input.send_keys(password)
                logging.info(f"✓ Entered password")
                time.sleep(0.5)  # Wait for password validation

                # Click Next button using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after password"):
                    logging.error("Could not find Next button after password")
                    self._take_screenshot(driver, "keepopen_error_next_button_step2")
                    return {'driver': driver, 'error': 'No Next button found after password'}
                
                time.sleep(1)  # Wait for next page to load

            except Exception as e:
                logging.error(f"Failed at step 2 (password): {e}")
                self._take_screenshot(driver, "keepopen_error_step2")
                return {'driver': driver, 'error': str(e)}

            # STEP 3: Enter Country and DOB (SAME robust logic as create_account)
            logging.info("Step 3: Entering Country and DOB...")
            time.sleep(1)
            self._take_screenshot(driver, "keepopen_step3_country_dob_page")

            try:
                # Try to find and select Country dropdown (optional)
                country_found = False
                country_selectors = [
                    (By.ID, "Country"),
                    (By.NAME, "Country"),
                    (By.CSS_SELECTOR, "select[name='Country']")
                ]

                for selector_type, selector_value in country_selectors:
                    try:
                        country_select = Select(driver.find_element(selector_type, selector_value))
                        country_select.select_by_value("US")
                        logging.info("✓ Selected country: US")
                        country_found = True
                        break
                    except:
                        continue

                if not country_found:
                    logging.info("No country field found (may not be required)")

                # Enter birth date - Using improved selectors based on TypeScript reference (same as create_account)
                dob_entered = False

                try:
                    logging.info("Waiting for DOB fields to load...")
                    time.sleep(1.5)

                    # DAY - Improved selectors (Portuguese and English, with IDs)
                    day_selectors = [
                        (By.ID, "BirthDayDropdown"),
                        (By.CSS_SELECTOR, "select[id='BirthDayDropdown']"),
                        (By.CSS_SELECTOR, "combobox[id='BirthDayDropdown']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Day' i]"),
                        (By.NAME, "BirthDay"),
                        (By.CSS_SELECTOR, "select[name='BirthDay']"),
                        (By.CSS_SELECTOR, "select[id='BirthDay']"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "div[aria-label*='Dia' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Day' i]"),
                    ]

                    day_element = None
                    for selector_type, selector_value in day_selectors:
                        try:
                            day_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            logging.info(f"✓ Found day field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not day_element:
                        raise Exception("Could not find Day field")

                    tag_name = day_element.tag_name.lower()
                    day_selected = False

                    if tag_name == 'select':
                        select = Select(day_element)
                        try:
                            select.select_by_value(str(birth_day))
                            day_selected = True
                            logging.info(f"✓ Selected day {birth_day} via Select")
                        except:
                            try:
                                select.select_by_visible_text(str(birth_day))
                                day_selected = True
                                logging.info(f"✓ Selected day {birth_day} via visible text")
                            except Exception as e:
                                logging.error(f"Error selecting day via Select: {e}")
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", day_element)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", day_element)
                        time.sleep(0.5)

                        day_value = str(birth_day)
                        day_option_selectors = [
                            (By.XPATH, f"//*[@role='option'][@aria-label='{day_value}']"),
                            (By.XPATH, f"//*[@role='option'][text()='{day_value}']"),
                            (By.XPATH, f"//option[@value='{day_value}']"),
                            (By.XPATH, f"//li[text()='{day_value}']"),
                            (By.XPATH, f"//div[text()='{day_value}']"),
                            (By.XPATH, f"//*[text()='{day_value}']"),
                        ]

                        for opt_type, opt_value in day_option_selectors:
                            try:
                                day_option = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((opt_type, opt_value))
                                )
                                day_option.click()
                                day_selected = True
                                logging.info(f"✓ Selected day {day_value}")
                                break
                            except:
                                continue

                        if not day_selected:
                            clicked = driver.execute_script("""
                                const options = Array.from(document.querySelectorAll('[role="option"], option, li, div'));
                                const dayOption = options.find(opt => {
                                    const text = opt.textContent?.trim();
                                    const ariaLabel = opt.getAttribute('aria-label');
                                    return text === arguments[0] || ariaLabel === arguments[0];
                                });
                                if (dayOption) {
                                    dayOption.click();
                                    return true;
                                }
                                return false;
                            """, day_value)
                            if clicked:
                                day_selected = True
                                logging.info(f"✓ Selected day {day_value} via JavaScript")

                    if not day_selected:
                        raise Exception(f"Could not select day {birth_day}")

                    time.sleep(0.3)

                    # MONTH - Improved selectors with Portuguese month names
                    month_selectors = [
                        (By.ID, "BirthMonthDropdown"),
                        (By.CSS_SELECTOR, "select[id='BirthMonthDropdown']"),
                        (By.CSS_SELECTOR, "combobox[id='BirthMonthDropdown']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Month' i]"),
                        (By.NAME, "BirthMonth"),
                        (By.CSS_SELECTOR, "select[name='BirthMonth']"),
                        (By.CSS_SELECTOR, "select[id='BirthMonth']"),
                        (By.CSS_SELECTOR, "button[aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "div[aria-label*='Mês' i]"),
                        (By.CSS_SELECTOR, "button[aria-label*='Month' i]"),
                    ]

                    month_names_pt = ['', 'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
                                      'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']
                    month_names_en = ['', 'January', 'February', 'March', 'April', 'May', 'June',
                                     'July', 'August', 'September', 'October', 'November', 'December']
                    
                    month_name_pt = month_names_pt[birth_month]
                    month_name_en = month_names_en[birth_month]
                    month_num = str(birth_month)

                    month_element = None
                    for selector_type, selector_value in month_selectors:
                        try:
                            month_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            logging.info(f"✓ Found month field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not month_element:
                        raise Exception("Could not find Month field")

                    tag_name = month_element.tag_name.lower()
                    month_selected = False

                    if tag_name == 'select':
                        select = Select(month_element)
                        try:
                            select.select_by_value(month_num)
                            month_selected = True
                            logging.info(f"✓ Selected month {month_num} via Select")
                        except:
                            try:
                                select.select_by_visible_text(month_name_pt)
                                month_selected = True
                                logging.info(f"✓ Selected month {month_name_pt} via Select")
                            except:
                                try:
                                    select.select_by_visible_text(month_name_en)
                                    month_selected = True
                                    logging.info(f"✓ Selected month {month_name_en} via Select")
                                except Exception as e:
                                    logging.error(f"Error selecting month via Select: {e}")
                    else:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", month_element)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", month_element)
                        time.sleep(0.5)

                        month_option_selectors = [
                            (By.XPATH, f"//*[@role='option'][contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//*[@role='option'][contains(text(), '{month_name_en}')]"),
                            (By.XPATH, f"//*[@role='option'][text()='{month_num}']"),
                            (By.XPATH, f"//*[contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//*[contains(text(), '{month_name_en}')]"),
                            (By.XPATH, f"//li[contains(text(), '{month_name_pt}')]"),
                            (By.XPATH, f"//div[contains(text(), '{month_name_pt}')]"),
                        ]

                        for opt_type, opt_value in month_option_selectors:
                            try:
                                month_option = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((opt_type, opt_value))
                                )
                                month_option.click()
                                month_selected = True
                                logging.info(f"✓ Selected month {month_name_pt}")
                                break
                            except:
                                continue

                        if not month_selected:
                            clicked = driver.execute_script("""
                                const options = Array.from(document.querySelectorAll('[role="option"], option, li, div'));
                                const monthOption = options.find(opt => {
                                    const text = opt.textContent?.toLowerCase().trim();
                                    return text.includes(arguments[0].toLowerCase()) || text === arguments[1];
                                });
                                if (monthOption) {
                                    monthOption.click();
                                    return true;
                                }
                                return false;
                            """, month_name_pt, month_num)
                            if clicked:
                                month_selected = True
                                logging.info(f"✓ Selected month via JavaScript")

                    if not month_selected:
                        raise Exception(f"Could not select month {birth_month}")

                    time.sleep(0.3)

                    # YEAR - Improved selectors
                    year_selectors = [
                        (By.NAME, "BirthYear"),
                        (By.ID, "BirthYear"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[type='number'][aria-label*='Year' i]"),
                        (By.CSS_SELECTOR, "select[name='BirthYear']"),
                        (By.CSS_SELECTOR, "select[id='BirthYear']"),
                        (By.CSS_SELECTOR, "[role='combobox'][aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[aria-label*='Ano' i]"),
                        (By.CSS_SELECTOR, "input[aria-label*='Year' i]"),
                    ]

                    year_element = None
                    for selector_type, selector_value in year_selectors:
                        try:
                            year_element = wait_short.until(
                                EC.presence_of_element_located((selector_type, selector_value))
                            )
                            logging.info(f"✓ Found year field with: {selector_type} = {selector_value}")
                            break
                        except:
                            continue

                    if not year_element:
                        raise Exception("Could not find Year field")

                    tag_name = year_element.tag_name.lower()
                    year_filled = False

                    if tag_name == 'select':
                        select = Select(year_element)
                        select.select_by_value(str(birth_year))
                        year_filled = True
                        logging.info(f"✓ Selected year {birth_year} via Select")
                    else:
                        year_element.clear()
                        year_element.send_keys(str(birth_year))
                        year_filled = True
                        logging.info(f"✓ Entered year {birth_year}")

                    if not year_filled:
                        raise Exception(f"Could not fill year {birth_year}")

                    dob_entered = True
                    logging.info(f"✓ Successfully entered DOB: {birth_day}/{birth_month}/{birth_year}")

                except Exception as e:
                    logging.error(f"Error entering DOB: {e}")
                    self._take_screenshot(driver, "keepopen_error_dob_entry")

                if not dob_entered:
                    logging.error("CRITICAL: Could not enter DOB")
                    return {'driver': driver, 'error': 'Failed to enter DOB'}

                time.sleep(1)  # Give page time to be ready for Next button

                # Click Next button after DOB using helper method (supports Portuguese and English)
                if not self._click_next_button(driver, wait_time=5, context="after DOB"):
                    logging.warning("Could not auto-click Next button after DOB")
                    logging.warning("Please manually click Next button...")
                    self._take_screenshot(driver, "keepopen_manual_next_needed")
                    # Wait up to 30 seconds for manual click
                    logging.info("Waiting 30 seconds for manual Next click...")
                    time.sleep(30)
                else:
                    time.sleep(2)  # Wait for page to navigate

            except Exception as e:
                logging.error(f"Failed at step 3 (DOB): {e}")
                self._take_screenshot(driver, "keepopen_error_step3")

            # STEP 4: Enter name (SAME logic as create_account)
            logging.info("Step 4: Checking for name fields or CAPTCHA...")
            time.sleep(1.5)  # Give page time to load
            self._take_screenshot(driver, "keepopen_step4_name_page")
            logging.info(f"Current URL: {driver.current_url}")

            try:
                # Check if we're on the name page by looking for URL pattern
                current_url = driver.current_url
                if "signup.live.com" in current_url and "lic=1" in current_url:
                    logging.info("On name entry page (detected lic=1 parameter)")
                
                # Try to find first name - with longer wait time
                first_name_input = None
                first_name_selectors = [
                    (By.CSS_SELECTOR, "input[aria-label*='First' i]"),
                    (By.NAME, "FirstName"),
                    (By.ID, "FirstName"),
                    (By.CSS_SELECTOR, "input[name='FirstName']"),
                    (By.CSS_SELECTOR, "input[type='text']:first-of-type"),
                    (By.XPATH, "//input[@type='text'][1]"),
                ]

                for selector_type, selector_value in first_name_selectors:
                    try:
                        # Use longer wait for name fields
                        first_name_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((selector_type, selector_value))
                        )
                        # Scroll into view
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", first_name_input)
                        time.sleep(0.3)
                        first_name_input.clear()
                        first_name_input.send_keys(first_name)
                        logging.info(f"✓ Entered first name: {first_name} using: {selector_type}")
                        time.sleep(0.5)
                        break
                    except Exception as e:
                        logging.debug(f"First name selector {selector_type} failed: {e}")
                        continue

                if not first_name_input:
                    logging.warning("Could not find first name field - checking if on CAPTCHA page...")
                    # Check if we're actually on CAPTCHA instead
                    page_text = driver.find_element(By.TAG_NAME, "body").text
                    if "prove you're human" in page_text.lower() or "captcha" in page_text.lower():
                        logging.info("Actually on CAPTCHA page - skipping name step")
                    else:
                        logging.error("No first name field found and not on CAPTCHA page!")
                        self._take_screenshot(driver, "keepopen_no_name_field")
                else:
                    # First name entered successfully - now try last name
                    last_name_input = None
                    time.sleep(0.5)
                    
                    # Method 1: Try all text inputs and pick the 2nd one
                    text_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='text']")
                    logging.info(f"Found {len(text_inputs)} text input fields")
                    
                    if len(text_inputs) >= 2:
                        last_name_input = text_inputs[1]
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_name_input)
                        time.sleep(0.3)
                        last_name_input.clear()
                        last_name_input.send_keys(last_name)
                        logging.info(f"✓ Entered last name: {last_name} (using 2nd text input)")
                    else:
                        # Method 2: Try specific selectors
                        last_name_selectors = [
                            (By.CSS_SELECTOR, "input[aria-label*='Last' i]"),
                            (By.NAME, "LastName"),
                            (By.ID, "LastName"),
                            (By.CSS_SELECTOR, "input[name='LastName']"),
                        ]
                        
                        for selector_type, selector_value in last_name_selectors:
                            try:
                                last_name_input = driver.find_element(selector_type, selector_value)
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", last_name_input)
                                time.sleep(0.3)
                                last_name_input.clear()
                                last_name_input.send_keys(last_name)
                                logging.info(f"✓ Entered last name: {last_name} using: {selector_type}")
                                break
                            except:
                                continue
                    
                    if not last_name_input:
                        logging.warning("Could not find last name field - may not be required")

                    time.sleep(1)  # Give page time to process

                    # Click Next button after name entry using helper method (supports Portuguese and English)
                    if not self._click_next_button(driver, wait_time=5, context="after name"):
                        logging.warning("Could not auto-click Next after name entry")
                        logging.warning("Please manually click Next button...")
                        self._take_screenshot(driver, "keepopen_manual_next_after_name")
                        time.sleep(30)  # Wait for manual click
                    else:
                        time.sleep(2)  # Wait for navigation

            except Exception as e:
                logging.warning(f"Issue at step 4 (name): {e}")
                self._take_screenshot(driver, "keepopen_error_step4")

            # STEP 5: Handle CAPTCHA (SAME logic as create_account)
            logging.info("Step 5: Checking for CAPTCHA...")
            time.sleep(1.5)
            self._take_screenshot(driver, "keepopen_step5_captcha_check")

            # Check for CAPTCHA (multiple detection methods)
            captcha_detected = False
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text
                if "prove you're human" in page_text.lower() or "let's prove" in page_text.lower():
                    captcha_detected = True
                    logging.warning("⚠ CAPTCHA detected (modern interactive CAPTCHA)!")
                elif driver.find_elements(By.ID, "enforcementFrame"):
                    captcha_detected = True
                    logging.warning("⚠ CAPTCHA detected (enforcement frame)!")
            except:
                pass

            if captcha_detected:
                logging.warning("=" * 60)
                logging.warning("MANUAL CAPTCHA SOLVING REQUIRED")
                logging.warning("Please solve the CAPTCHA in the browser window")
                logging.warning("Waiting up to 3 minutes for you to complete it...")
                logging.warning("=" * 60)

                # Wait up to 3 minutes for CAPTCHA to be solved
                max_wait = 180
                start_time = time.time()

                while (time.time() - start_time) < max_wait:
                    time.sleep(2)
                    try:
                        current_url = driver.current_url
                        page_text = driver.find_element(By.TAG_NAME, "body").text

                        if "prove you're human" not in page_text.lower() and \
                           "let's prove" not in page_text.lower():
                            logging.info("✓ CAPTCHA appears to be solved! Continuing...")
                            time.sleep(2)
                            break
                    except:
                        pass
                else:
                    logging.error("CAPTCHA not solved within 3 minute timeout")
                    self._take_screenshot(driver, "keepopen_captcha_timeout")
                    return {
                        'driver': driver,
                        'email': email,
                        'password': password,
                        'first_name': first_name,
                        'last_name': last_name,
                        'birth_date': birth_date,
                        'error': 'CAPTCHA timeout'
                    }
            else:
                logging.info("No CAPTCHA detected, continuing...")

            # STEP 6: Verify account creation success
            logging.info("Verifying account creation...")
            time.sleep(2)  # Give page time to settle
            self._take_screenshot(driver, "keepopen_final_page")

            current_url = driver.current_url
            logging.info(f"Final URL: {current_url}")
            
            # Check if we're STILL on the name page (lic=1)
            if "signup.live.com" in current_url and "lic=1" in current_url:
                logging.error("="*60)
                logging.error("STILL ON NAME PAGE!")
                logging.error("The name entry step may have failed.")
                logging.error("Please complete the following manually:")
                logging.error("1. Enter First Name and Last Name")
                logging.error("2. Click Next button")
                logging.error("Waiting 60 seconds for manual completion...")
                logging.error("="*60)
                
                # Wait for manual completion
                for i in range(12):  # 12 x 5 seconds = 60 seconds
                    time.sleep(5)
                    current_url = driver.current_url
                    
                    # Check if we moved past the name page
                    if "lic=1" not in current_url:
                        logging.info(f"✓ Moved past name page! New URL: {current_url}")
                        break
                    
                    if i % 3 == 0:
                        logging.info(f"Still waiting for name page completion... ({(i+1)*5}s elapsed)")
                
                # Update current URL after waiting
                current_url = driver.current_url
                logging.info(f"URL after manual intervention: {current_url}")
            
            # Also log page title for debugging
            try:
                page_title = driver.title
                logging.info(f"Page title: {page_title}")
            except:
                page_title = "Unknown"

            # Success indicators - expanded list
            success_indicators = [
                "outlook.live.com",
                "outlook.office.com", 
                "account.microsoft.com",
                "signup.live.com/proofs",  # Proofs page (phone verification step - still success)
                "/signup?wa=wsignin",
                "login.live.com/login",  # Sometimes redirects here after success
            ]

            # Check current state
            is_success = any(indicator in current_url for indicator in success_indicators)
            
            # Also check if page text indicates success
            try:
                page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
                if any(phrase in page_text for phrase in ["welcome", "you're all set", "inbox", "get started"]):
                    is_success = True
                    logging.info("✓ Success detected from page content")
            except:
                pass

            if is_success:
                logging.info(f"✓ Account created successfully: {email}")
                logging.info("✓ Browser kept open - staying logged in")

                return {
                    'driver': driver,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': birth_date,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                # Not clearly at success page - give manual intervention time
                logging.warning("="*60)
                logging.warning(f"Current URL doesn't match expected success patterns")
                logging.warning(f"URL: {current_url}")
                logging.warning("Waiting 60 seconds for manual intervention...")
                logging.warning("Please complete any remaining steps manually")
                logging.warning("="*60)
                
                # Wait and check periodically
                for i in range(12):  # 12 x 5 seconds = 60 seconds
                    time.sleep(5)
                    current_url = driver.current_url
                    
                    # Check if URL changed to success page
                    if any(indicator in current_url for indicator in success_indicators):
                        logging.info(f"✓ Account created successfully after manual intervention: {email}")
                        logging.info(f"Final URL: {current_url}")
                        return {
                            'driver': driver,
                            'email': email,
                            'password': password,
                            'first_name': first_name,
                            'last_name': last_name,
                            'birth_date': birth_date,
                            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    
                    if i % 3 == 0:  # Log every 15 seconds
                        logging.info(f"Still waiting... ({(i+1)*5}s elapsed)")

                # After 60 seconds, return what we have
                logging.warning(f"Manual intervention timeout. Final URL: {current_url}")
                self._take_screenshot(driver, "keepopen_manual_timeout")
                
                # Return account data anyway - caller can decide what to do
                return {
                    'driver': driver,
                    'email': email,
                    'password': password,
                    'first_name': first_name,
                    'last_name': last_name,
                    'birth_date': birth_date,
                    'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

        except TimeoutException as e:
            logging.error(f"Timeout creating account: {e}")
            if driver:
                self._take_screenshot(driver, "error_timeout")
                # Return driver even on error so caller can handle cleanup
                return {
                    'driver': driver,
                    'email': None,
                    'password': None,
                    'first_name': None,
                    'last_name': None,
                    'birth_date': None,
                    'error': str(e)
                }
            return None

        except Exception as e:
            logging.error(f"Exception creating Outlook account: {e}")
            if driver:
                self._take_screenshot(driver, "error_exception")
                # Return driver even on error so caller can handle cleanup
                return {
                    'driver': driver,
                    'email': None,
                    'password': None,
                    'first_name': None,
                    'last_name': None,
                    'birth_date': None,
                    'error': str(e)
                }
            return None

        # NOTE: No finally block that closes driver!
        # Caller is responsible for closing the driver when done

    def _click_next_button(self, driver, wait_time: int = 5, context: str = ""):
        """
        Helper method to click Next/Avançar button supporting both Portuguese and English
        
        Args:
            driver: Selenium WebDriver instance
            wait_time: Maximum time to wait for button to be clickable
            context: Context description for logging (e.g., "after password")
        
        Returns:
            True if button was clicked successfully, False otherwise
        """
        next_button = None
        wait = WebDriverWait(driver, wait_time)
        
        # Try multiple selectors including both English and Portuguese
        next_selectors = [
            (By.ID, "iSignupAction"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "input[type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Next')]"),  # English
            (By.XPATH, "//button[contains(text(), 'Avançar')]"),  # Portuguese
            (By.XPATH, "//button[contains(@class, 'fui-Button') and contains(text(), 'Avançar')]"),  # Portuguese with class
            (By.XPATH, "//button[contains(@class, 'fui-Button') and contains(text(), 'Next')]"),  # English with class
            (By.CSS_SELECTOR, "button.fui-Button"),  # Any button with fui-Button class
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//input[@value='Next']"),
            (By.XPATH, "//input[@value='Avançar']"),
        ]
        
        for selector_type, selector_value in next_selectors:
            try:
                next_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
                time.sleep(0.2)
                
                # Try normal click first
                try:
                    next_button.click()
                    logging.info(f"✓ Clicked Next button{(' ' + context) if context else ''} using: {selector_type} = {selector_value}")
                    return True
                except:
                    # Fallback to JavaScript click
                    driver.execute_script("arguments[0].click();", next_button)
                    logging.info(f"✓ Clicked Next button{(' ' + context) if context else ''} (JS click) using: {selector_type} = {selector_value}")
                    return True
            except Exception as e:
                logging.debug(f"Selector {selector_type} = {selector_value} failed: {e}")
                continue
        
        # Fallback: Search all buttons for text
        if not next_button:
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                for btn in all_buttons:
                    try:
                        btn_text = btn.text.strip()
                        if btn_text in ["Next", "Avançar"] or "Avançar" in btn_text or "Next" in btn_text:
                            if btn.is_displayed() and btn.is_enabled():
                                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
                                time.sleep(0.2)
                                driver.execute_script("arguments[0].click();", btn)
                                logging.info(f"✓ Clicked Next button{(' ' + context) if context else ''} using fallback (text: {btn_text})")
                                return True
                    except:
                        continue
            except Exception as e:
                logging.debug(f"Fallback button search failed: {e}")
        
        return False

    def _take_screenshot(self, driver, name: str):
        """Take screenshot for debugging"""
        try:
            import os
            os.makedirs("screenshots", exist_ok=True)
            filename = f"screenshots/{name}_{int(time.time())}.png"
            driver.save_screenshot(filename)
            logging.info(f"Screenshot saved: {filename}")
        except Exception as e:
            logging.error(f"Failed to save screenshot: {e}")

    def create_bulk_accounts(
        self,
        count: int,
        output_file: str = "outlook_accounts.csv",
        proxy_list: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Create multiple Outlook accounts

        Args:
            count: Number of accounts to create
            output_file: CSV file to save account details
            proxy_list: List of proxies to rotate through (optional)

        Returns:
            List of created account dictionaries
        """
        accounts = []

        # Check if file exists to determine if we need to write header
        import os
        file_exists = os.path.exists(output_file)

        # Create CSV file with headers only if file doesn't exist
        if not file_exists:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Email', 'Password', 'First Name', 'Last Name', 'Birth Date'
                ])
            logging.info(f"Created new CSV file: {output_file}")
        else:
            logging.info(f"Appending to existing CSV file: {output_file}")

        logging.info(f"Creating {count} Outlook accounts...")
        if proxy_list:
            logging.info(f"Using {len(proxy_list)} proxies for account creation")

        for i in range(count):
            logging.info(f"\n[{i+1}/{count}] Creating account...")

            # Get proxy for this account if list provided
            proxy = None
            if proxy_list and len(proxy_list) > 0:
                proxy = proxy_list[i % len(proxy_list)]
                logging.info(f"Using proxy: {proxy}")

            account = self.create_account(proxy=proxy)

            if account:
                accounts.append(account)

                # Save to CSV
                with open(output_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        account['email'],
                        account['password'],
                        account['first_name'],
                        account['last_name'],
                        account['birth_date']
                    ])

                logging.info(f"✓ Progress: {len(accounts)}/{count} accounts created")
            else:
                logging.error(f"✗ Failed to create account {i+1}")

            # No delay between accounts - create as fast as possible
            # Each account creation already has built-in delays for page loads

        logging.info(f"\n{'='*60}")
        logging.info(f"Account Creation Complete!")
        logging.info(f"Successfully created: {len(accounts)}/{count} accounts")
        logging.info(f"Saved to: {output_file}")
        logging.info(f"{'='*60}\n")

        return accounts


def main():
    """Main function for standalone usage"""
    print("\n" + "="*60)
    print("OUTLOOK EMAIL ACCOUNT CREATOR")
    print("="*60)
    print("Creates Outlook/Hotmail email accounts")
    print("="*60 + "\n")

    creator = OutlookAccountCreator(headless=False)  # Non-headless for CAPTCHA solving

    # Ask user how many accounts to create
    try:
        count = int(input("How many email accounts to create? "))
        if count <= 0:
            print("Invalid number. Exiting.")
            return

        output_file = input("Output CSV file name (default: outlook_accounts.csv): ").strip()
        if not output_file:
            output_file = "outlook_accounts.csv"

        # Create accounts
        accounts = creator.create_bulk_accounts(count, output_file)

        # Display summary
        if accounts:
            print("\n" + "="*60)
            print("SAMPLE CREATED ACCOUNTS:")
            print("="*60)
            for i, acc in enumerate(accounts[:5], 1):  # Show first 5
                print(f"{i}. {acc['email']}")
                print(f"   Name: {acc['first_name']} {acc['last_name']}")

            if len(accounts) > 5:
                print(f"   ... and {len(accounts) - 5} more")

            print("="*60 + "\n")

    except KeyboardInterrupt:
        print("\n\nAborted by user.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        logging.error(f"Error in main: {e}")


if __name__ == "__main__":
    main()
