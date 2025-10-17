import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import time
import random
import os
import sys
import pickle


# Login credentials
EMAIL = "jacob@sfsolutions-usa.com"
PASSWORD = "Omnamahshiv@123"
LOGIN_URL = "https://carriersource.io/login"

def create_driver():
    """Create and return an undetected Chrome instance"""
    try:
        options = uc.ChromeOptions()
        
        # Essential arguments for cloud deployment (Render, Heroku, etc.)
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--headless')  # Run headless on cloud platforms
        options.add_argument('--window-size=1920,1080')
        
        # Additional stability arguments
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Speed up loading
        options.add_argument('--disable-javascript')  # May need to remove if JS is required
        
        # Set user agent to avoid detection
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Check if we're running on a cloud platform
        is_cloud = os.environ.get('RENDER', False) or os.environ.get('DYNO', False) or os.environ.get('VERCEL', False)
        
        if is_cloud:
            # For cloud platforms, try to find Chrome binary
            chrome_paths = [
                '/usr/bin/google-chrome',
                '/usr/bin/google-chrome-stable',
                '/usr/bin/chromium-browser',
                '/usr/bin/chromium',
                '/opt/google/chrome/chrome',
                '/usr/local/bin/chrome',
                '/usr/local/bin/google-chrome'
            ]
            
            chrome_binary_path = None
            for path in chrome_paths:
                if os.path.exists(path):
                    chrome_binary_path = path
                    print(f"Found Chrome binary at: {path}")
                    break
            
            if chrome_binary_path:
                options.binary_location = chrome_binary_path
            else:
                print("Warning: Chrome binary not found, using default configuration")
        
        # Try to create undetected Chrome driver first
        try:
            driver = uc.Chrome(
                options=options,
                driver_executable_path=None,
                browser_executable_path=None,
                suppress_welcome=True,
                use_subprocess=True,
                version_main=None  # Let undetected-chromedriver auto-detect
            )
            print("Successfully created undetected Chrome driver")
        except Exception as uc_error:
            print(f"Failed to create undetected Chrome driver: {uc_error}")
            print("Falling back to regular Chrome driver...")
            
            # Fallback to regular Chrome driver
            driver = webdriver.Chrome(options=options)
            print("Successfully created regular Chrome driver")
        
        # Set window size explicitly
        driver.set_window_size(1920, 1080)
        
        return driver
    except Exception as e:
        print(f"Error creating driver: {str(e)}")
        return None

def random_delay(min_seconds=1, max_seconds=3):
    """Add random delay between actions to appear more human-like"""
    time.sleep(random.uniform(min_seconds, max_seconds))

def type_slowly(element, text):
    """Type text into element with random delays"""
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.3))
def save_cookies(driver, path="cookies.pkl"):
    pickle.dump(driver.get_cookies(), open(path, "wb"))

def load_cookies(driver, path="cookies.pkl"):
    import os
    if os.path.exists(path):
        cookies = pickle.load(open(path, "rb"))
        for cookie in cookies:
            driver.add_cookie(cookie)
        return True
    return False

def login(driver):
    """Handle the login process"""
    try:
        print("Attempting to log in...")
        driver.get(LOGIN_URL)
        random_delay(3, 5)
        
        wait = WebDriverWait(driver, 20)
        
        # Find and fill email field
        print("Looking for email field...")
        email_field = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='email']")))
        print("Found email field, entering email...")
        
        # Clear field and ensure it's ready for input
        email_field.clear()
        random_delay(1, 2)
        ActionChains(driver).move_to_element(email_field).click().perform()
        random_delay(1, 2)
        type_slowly(email_field, EMAIL)
        random_delay(1, 2)
        
        # Find and fill password field
        print("Looking for password field...")
        password_field = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='password']")))
        print("Found password field, entering password...")
        
        # Clear field and ensure it's ready for input
        password_field.clear()
        random_delay(1, 2)
        ActionChains(driver).move_to_element(password_field).click().perform()
        random_delay(1, 2)
        type_slowly(password_field, PASSWORD)
        random_delay(2, 3)
        
        # Try multiple approaches to find and click the login button
        print("Looking for sign in button...")
        button_found = False
        
        # Try different button selectors
        button_selectors = [
            "button.btn.default.primary.x-btn-sign-in",
            "form[method='post'] button[type='submit']",
            "//button[contains(text(), 'Sign in')]",
            "//button[@type='submit']"
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith("//"):
                    login_button = wait.until(EC.element_to_be_clickable(
                        (By.XPATH, selector)))
                else:
                    login_button = wait.until(EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, selector)))
                
                # Ensure button is in view and clickable
                driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
                random_delay(1, 2)
                
                # Try both click methods
                try:
                    login_button.click()
                except:
                    ActionChains(driver).move_to_element(login_button).click().perform()
                
                button_found = True
                print("Successfully clicked sign in button")
                break
            except Exception as e:
                print(f"Failed with selector {selector}: {str(e)}")
                continue
        
        if not button_found:
            print("Could not find or click any login button")
            return False
        
        # Wait for login to complete and verify
        random_delay(5, 7)
        
        # Check if we're still on login page
        if "login" in driver.current_url.lower():
            print("Login failed - still on login page")
            if hasattr(driver, 'save_screenshot'):
                driver.save_screenshot("login_failed.png")
            return False
            
        print("Login successful!")
        return True
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        if hasattr(driver, 'save_screenshot'):
            driver.save_screenshot("login_error.png")
        return False

def check_login_required(driver):
    """Check if login is required by looking for sign-in elements"""
    try:
        # Check for sign-in button
        sign_in_buttons = driver.find_elements(By.CSS_SELECTOR, "button.btn.default.primary.x-btn-sign-in")
        if sign_in_buttons and sign_in_buttons[0].is_displayed():
            return True
            
        # Check if URL contains login
        if "login" in driver.current_url.lower():
            return True
            
        return False
    except:
        return False

def close_modal_safely(driver):
    """Safely close any open modal"""
    try:
        # Try multiple methods to close modal
        close_selectors = [
            "button[type='button'][aria-label='Close']",
            "button.close",
            ".modal-close",
            "button[data-dismiss='modal']"
        ]
        
        for selector in close_selectors:
            try:
                close_button = driver.find_element(By.CSS_SELECTOR, selector)
                if close_button.is_displayed():
                    close_button.click()
                    random_delay(1, 2)
                    return True
            except:
                continue
                
        # If no close button found, try clicking outside modal
        try:
            action = ActionChains(driver)
            action.move_by_offset(50, 50).click().perform()
            random_delay(1, 2)
            return True
        except:
            pass
            
        # Try pressing escape key
        try:
            ActionChains(driver).send_keys('\ue00c').perform()  # ESC key
            random_delay(1, 2)
            return True
        except:
            pass
            
        return False
    except Exception as e:
        print(f"Error closing modal: {str(e)}")
        return False

def handle_contact_with_session_refresh(driver, company, wait, company_index, current_url):
    """Handle the specific case where contact button requires sign-in after page refresh"""
    try:
        print("Handling contact button with session refresh...")
        
        # First refresh the page
        driver.refresh()
        random_delay(3, 5)
        
        # Check if login is required after refresh
        if check_login_required(driver):
            print("Login required after refresh, attempting to login...")
            if not login(driver):
                print("Failed to login after refresh")
                return "Login failed", "Login failed", "Login failed"
        
        # Navigate back to the target URL
        driver.get(current_url)
        random_delay(5, 7)
        
        # Wait for page to load completely
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='carrier_']")))
        except:
            print("Page didn't load properly after navigation")
            return "Page load failed", "Page load failed", "Page load failed"
        
        # Re-find companies after refresh
        company_selectors = [
            "div[id^='carrier_']",
            "div[class*='border-gray-300']",
            "div[class*='p-6']",
            "div[class*='bg-primary-50']",
            "article",
            ".carrier-item",
            ".company-item"
        ]
        
        companies = []
        for selector in company_selectors:
            try:
                companies = driver.find_elements(By.CSS_SELECTOR, selector)
                if companies:
                    break
            except:
                continue
        
        if company_index >= len(companies):
            print(f"Company index {company_index} out of range after refresh")
            return "Index error", "Index error", "Index error"
            
        company = companies[company_index]
        
        # Now try to click contact button again
        contact_selectors = [
            "button.x-link-contact",
            "a.x-link-contact", 
            "button.btn.hollow.primary.w-full.justify-center",
            "//button[contains(text(), 'Contact')]",
            "//a[contains(text(), 'Contact')]"
        ]
        
        contact_button = None
        for selector in contact_selectors:
            try:
                if selector.startswith("//"):
                    contact_button = company.find_element(By.XPATH, selector)
                else:
                    contact_button = company.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
                
        if not contact_button:
            print("No contact button found after refresh")
            return "No contact button", "No contact button", "No contact button"
        
        # Click contact button with better error handling
        contact_clicked = False
        try:
            # Scroll to button first
            driver.execute_script("arguments[0].scrollIntoView(true);", contact_button)
            random_delay(1, 2)
            
            # Try JavaScript click first
            driver.execute_script("arguments[0].click();", contact_button)
            contact_clicked = True
            print("Contact button clicked via JavaScript after refresh")
        except Exception as e:
            print(f"JavaScript click failed: {str(e)}")
            try:
                # Try ActionChains click
                ActionChains(driver).move_to_element(contact_button).click().perform()
                contact_clicked = True
                print("Contact button clicked via ActionChains after refresh")
            except Exception as e2:
                print(f"ActionChains click failed: {str(e2)}")
                try:
                    # Try direct click
                    contact_button.click()
                    contact_clicked = True
                    print("Contact button clicked via direct click after refresh")
                except Exception as e3:
                    print(f"Direct click failed: {str(e3)}")
        
        if not contact_clicked:
            print("Failed to click contact button after refresh")
            return "Contact button click failed", "Contact button click failed", "Contact button click failed"
        
        random_delay(2, 3)
        
        # Check if sign-in is required again
        if check_login_required(driver):
            print("Still requires sign-in after refresh and contact click")
            return "Still requires sign-in", "Still requires sign-in", "Still requires sign-in"
        
        # Extract contact information from modal
        try:
            modal = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.space-y-2, div.border.border-gray-300.rounded-sm"
            )))
        except:
            print("No modal found after refresh")
            return "No modal", "No modal", "No modal"
        
        # Get owner name
        owner_name = "Not available"
        try:
            owner_element = modal.find_element(
                By.XPATH, 
                ".//dt[text()='Name']/following-sibling::dd"
            )
            owner_name = owner_element.text.strip()
        except:
            try:
                # Alternative selector for owner name
                owner_elements = modal.find_elements(By.XPATH, ".//dd")
                if owner_elements:
                    owner_name = owner_elements[0].text.strip()
            except:
                pass
                
        # Get phone number
        phone = "Not available"
        try:
            phone_element = modal.find_element(
                By.XPATH,
                ".//dt[text()='Phone']/following-sibling::dd/a"
            )
            phone = phone_element.text.strip()
        except:
            try:
                # Alternative selector for phone
                phone_elements = modal.find_elements(By.XPATH, ".//a[contains(@href, 'tel:')]")
                if phone_elements:
                    phone = phone_elements[0].text.strip()
            except:
                pass
                
        # Get email
        email = "Not available"
        try:
            email_element = modal.find_element(
                By.XPATH,
                ".//dt[text()='Email']/following-sibling::dd/a"
            )
            email = email_element.text.strip()
        except:
            try:
                # Alternative selector for email
                email_elements = modal.find_elements(By.XPATH, ".//a[contains(@href, 'mailto:')]")
                if email_elements:
                    email = email_elements[0].text.strip()
            except:
                pass
        
        print(f"Found contact info after refresh - Owner: {owner_name}, Phone: {phone}, Email: {email}")
        
        # Close modal
        close_modal_safely(driver)
        random_delay(1, 2)
        
        return owner_name, phone, email
        
    except Exception as e:
        print(f"Error in handle_contact_with_session_refresh: {str(e)}")
        return "Error", "Error", "Error"

def get_contact_info(driver, company, wait, company_index, current_url):
    """Get contact information with improved error handling and login management"""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1} to get contact info for company {company_index}")
            
            # Get company name for identification
            try:
                company_name = company.find_element(
                    By.CSS_SELECTOR, 
                    "h2[class*='text-lg']"
                ).text.strip()
            except:
                company_name = company.find_element(By.TAG_NAME, "h2").text.strip()

            print(f"Processing company: {company_name}")
            
            # Scroll to company element and click contact button
            driver.execute_script("arguments[0].scrollIntoView(true);", company)
            random_delay(1, 2)
            
            # Find contact button
            contact_selectors = [
                "button.x-link-contact",
                "a.x-link-contact", 
                "button.btn.hollow.primary.w-full.justify-center",
                "//button[contains(text(), 'Contact')]",
                "//a[contains(text(), 'Contact')]"
            ]
            
            contact_button = None
            for selector in contact_selectors:
                try:
                    if selector.startswith("//"):
                        contact_button = company.find_element(By.XPATH, selector)
                    else:
                        contact_button = company.find_element(By.CSS_SELECTOR, selector)
                    break
                except:
                    continue
                    
            if not contact_button:
                print(f"No contact button found for {company_name}")
                return "No contact button", "No contact button", "No contact button"
            
            # Click contact button
            try:
                driver.execute_script("arguments[0].click();", contact_button)
            except:
                ActionChains(driver).move_to_element(contact_button).click().perform()
            
            random_delay(2, 3)
            
            # Check if sign-in is required
            if check_login_required(driver):
                print(f"Login required for {company_name}, handling...")
                
                # Try clicking sign-in button first
                try:    
                    sign_in_button = driver.find_element(By.CSS_SELECTOR, "button.btn.default.primary.x-btn-sign-in")
                    if sign_in_button.is_displayed():
                        print("Clicking sign-in button...")
                        sign_in_button.click()
                        random_delay(2, 3)
                        
                        # Check if login form appeared
                        try:
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
                            print("Login form appeared, proceeding with login...")
                        except:
                            print("Sign-in button click didn't work, forcing refresh...")
                            if not force_refresh_and_relogin(driver, current_url):
                                print("Failed to recover from login issue")
                                return "Login failed", "Login failed", "Login failed"
                            
                            # Re-find companies after refresh
                            company_selectors = [
                                "div[id^='carrier_']",
                                "div[class*='border-gray-300']",
                                "div[class*='p-6']",
                                "div[class*='bg-primary-50']",
                                "article",
                                ".carrier-item",
                                ".company-item"
                            ]
                            
                            companies = []
                            for selector in company_selectors:
                                try:
                                    companies = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if companies:
                                        break
                                except:
                                    continue
                            
                            if company_index >= len(companies):
                                print(f"Company index {company_index} out of range after refresh")
                                return "Index error", "Index error", "Index error"
                                
                            company = companies[company_index]
                            continue  # Retry with refreshed state
                            
                except Exception as e:
                    print(f"Error with sign-in button: {str(e)}")
                    if not force_refresh_and_relogin(driver, current_url):
                        print("Failed to recover from login issue")
                        return "Login failed", "Login failed", "Login failed"
                    
                    # Re-find companies after refresh
                    company_selectors = [
                        "div[id^='carrier_']",
                        "div[class*='border-gray-300']",
                        "div[class*='p-6']",
                        "div[class*='bg-primary-50']",
                        "article",
                        ".carrier-item",
                        ".company-item"
                    ]
                    
                    companies = []
                    for selector in company_selectors:
                        try:
                            companies = driver.find_elements(By.CSS_SELECTOR, selector)
                            if companies:
                                break
                        except:
                            continue
                    
                    if company_index >= len(companies):
                        print(f"Company index {company_index} out of range after refresh")
                        return "Index error", "Index error", "Index error"
                        
                    company = companies[company_index]
                    continue  # Retry with refreshed state
                
                # Perform login
                if not login(driver):
                    print("Failed to login")
                    return "Login failed", "Login failed", "Login failed"
                
                # Navigate back to current page
                driver.get(current_url)
                random_delay(3, 5)
                
                # Re-find companies after login
                company_selectors = [
                    "div[id^='carrier_']",
                    "div[class*='border-gray-300']",
                    "div[class*='p-6']",
                    "div[class*='bg-primary-50']",
                    "article",
                    ".carrier-item",
                    ".company-item"
                ]
                
                companies = []
                for selector in company_selectors:
                    try:
                        companies = driver.find_elements(By.CSS_SELECTOR, selector)
                        if companies:
                            break
                    except:
                        continue
                
                if company_index >= len(companies):
                    print(f"Company index {company_index} out of range after login")
                    return "Index error", "Index error", "Index error"
                    
                company = companies[company_index]
                
                # Click contact button again after login
                driver.execute_script("arguments[0].scrollIntoView(true);", company)
                random_delay(1, 2)
                
                contact_button = None
                for selector in contact_selectors:
                    try:
                        if selector.startswith("//"):
                            contact_button = company.find_element(By.XPATH, selector)
                        else:
                            contact_button = company.find_element(By.CSS_SELECTOR, selector)
                        break
                    except:
                        continue
                        
                if not contact_button:
                    print(f"No contact button found after login for {company_name}")
                    return "No contact button", "No contact button", "No contact button"
                
                try:
                    driver.execute_script("arguments[0].click();", contact_button)
                except:
                    ActionChains(driver).move_to_element(contact_button).click().perform()
                
                random_delay(2, 3)
            
            # Extract contact information from modal
            try:
                modal = wait.until(EC.presence_of_element_located((
                    By.CSS_SELECTOR, "div.space-y-2, div.border.border-gray-300.rounded-sm"
                )))
            except:
                print(f"No modal found for {company_name} - contact information unavailable")
                print("Performing hard refresh and sign-in to recover...")
                
                # Use the session refresh handler
                return handle_contact_with_session_refresh(driver, company, wait, company_index, current_url)
            
            # Get owner name
            owner_name = "Not available"
            try:
                owner_element = modal.find_element(
                    By.XPATH, 
                    ".//dt[text()='Name']/following-sibling::dd"
                )
                owner_name = owner_element.text.strip()
            except:
                try:
                    # Alternative selector for owner name
                    owner_elements = modal.find_elements(By.XPATH, ".//dd")
                    if owner_elements:
                        owner_name = owner_elements[0].text.strip()
                except:
                    pass
                    
            # Get phone number
            phone = "Not available"
            try:
                phone_element = modal.find_element(
                    By.XPATH,
                    ".//dt[text()='Phone']/following-sibling::dd/a"
                )
                phone = phone_element.text.strip()
            except:
                try:
                    # Alternative selector for phone
                    phone_elements = modal.find_elements(By.XPATH, ".//a[contains(@href, 'tel:')]")
                    if phone_elements:
                        phone = phone_elements[0].text.strip()
                except:
                    pass
                    
            # Get email
            email = "Not available"
            try:
                email_element = modal.find_element(
                    By.XPATH,
                    ".//dt[text()='Email']/following-sibling::dd/a"
                )
                email = email_element.text.strip()
            except:
                try:
                    # Alternative selector for email
                    email_elements = modal.find_elements(By.XPATH, ".//a[contains(@href, 'mailto:')]")
                    if email_elements:
                        email = email_elements[0].text.strip()
                except:
                    pass
            
            print(f"Found contact info - Owner: {owner_name}, Phone: {phone}, Email: {email}")
            
            # Close modal
            close_modal_safely(driver)
            random_delay(1, 2)
            
            return owner_name, phone, email
            
        except Exception as e:
            print(f"Error getting contact information (attempt {attempt + 1}): {str(e)}")
            
            # Close any open modal before retrying
            close_modal_safely(driver)
            
            if attempt == max_attempts - 1:  # Last attempt
                print(f"Failed to get contact info for company {company_index} after {max_attempts} attempts")
                return "Error", "Error", "Error"
            
            # Force refresh and try again
            if not force_refresh_and_relogin(driver, current_url):
                print("Failed to recover, skipping this company")
                return "Recovery failed", "Recovery failed", "Recovery failed"
            
            # Re-find companies after refresh
            try:
                company_selectors = [
                    "div[id^='carrier_']",
                    "div[class*='border-gray-300']",
                    "div[class*='p-6']",
                    "div[class*='bg-primary-50']",
                    "article",
                    ".carrier-item",
                    ".company-item"
                ]
                
                companies = []
                for selector in company_selectors:
                    try:
                        companies = driver.find_elements(By.CSS_SELECTOR, selector)
                        if companies:
                            break
                    except:
                        continue
            except:
                print("Failed to re-find companies after refresh")
                return "Refresh error", "Refresh error", "Refresh error"
            
            try:
                if company_index >= len(companies):
                    print(f"Company index {company_index} out of range after refresh")
                    return "Index error", "Index error", "Index error"
                    
                company = companies[company_index]
            except:
                print("Failed to re-find companies after refresh")
                return "Refresh error", "Refresh error", "Refresh error"
    
    return "Max attempts exceeded", "Max attempts exceeded", "Max attempts exceeded"

def force_refresh_and_relogin(driver, target_url):
    """Force refresh the page and re-login if needed"""
    try:
        print("Force refreshing page and checking login status...")
        driver.refresh()
        random_delay(3, 5)
        
        if check_login_required(driver):
            print("Login required after refresh, attempting to login...")
            if not login(driver):
                print("Failed to login after refresh")
                return False
                
            # Navigate back to target URL
            driver.get(target_url)
            random_delay(3, 5)
            
        return True
    except Exception as e:
        print(f"Error in force refresh and relogin: {str(e)}")
        return False

def verify_page_loaded(driver, wait, expected_elements=None):
    """Verify that the page has loaded correctly"""
    try:
        print(f"Current URL: {driver.current_url}")
        print("Verifying page load...")
        
        # Check if we're on login page
        if "login" in driver.current_url.lower():
            print("Still on login page - authentication may have failed")
            return False
            
        # Wait for page to stabilize
        time.sleep(3)
        
        # Check for common page elements
        if expected_elements:
            for element_selector in expected_elements:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, element_selector)))
                    print(f"Found expected element: {element_selector}")
                    return True
                except TimeoutException:
                    print(f"Expected element not found: {element_selector}")
                    continue
        
        # Check for company listings
        try:
            # Try multiple selectors for company cards
            company_selectors = [
                "div[id^='carrier_']",
                "div[class*='border-gray-300']",
                "div[class*='p-6']",
                "div[class*='bg-primary-50']",
                "article",
                ".carrier-item",
                ".company-item"
            ]
            
            for selector in company_selectors:
                try:
                    companies = driver.find_elements(By.CSS_SELECTOR, selector)
                    if companies:
                        print(f"Found {len(companies)} companies on page using selector: {selector}")
                        return True
                except:
                    continue
        except:
            pass
            
        # Check for any content indicators
        try:
            # Look for pagination or results indicators
            pagination = driver.find_elements(By.CSS_SELECTOR, "nav[aria-label='pagination'], .pagination")
            if pagination:
                print("Found pagination - page appears to be loaded")
                return True
        except:
            pass
            
        print("Page verification failed - no expected content found")
        return False
        
    except Exception as e:
        print(f"Error verifying page load: {str(e)}")
        return False

# def scrape_company_data(url):
#     driver = create_driver()
#     if not driver:
#         print("Failed to create driver. Exiting...")
#         return []
        
#     companies_data = []
#     page = 1
#     max_retries = 3
    
#     try:
#         # Login first
#         if not login(driver):
#             print("Failed to log in. Exiting...")
#             return companies_data
#         save_cookies(driver)
    
#         # Navigate to the flatbed trucking companies page
#         print("Navigating to flatbed trucking companies page...")
#         driver.get(url)
#         random_delay(5, 7)  # Give enough time for the page to load
        
#         wait = WebDriverWait(driver, 30)
        
#         # Verify we're on the correct page using the new verification function
#         if not verify_page_loaded(driver, wait):
#             print("Page verification failed - trying to reload...")
#             # Try one more time with a fresh login
#             if not login(driver):
#                 print("Failed to re-login. Exiting...")
#                 return companies_data
            
#             driver.get(url)
#             random_delay(5, 7)
            
#             if not verify_page_loaded(driver, wait):
#                 print("Failed to load flatbed trucking companies page after retry")
#                 if hasattr(driver, 'save_screenshot'):
#                     driver.save_screenshot("page_load_failed.png")
#                 return companies_data
        
#         print("Successfully verified flatbed trucking companies page loaded")
            
#         while True:
#             print(f"Scraping page {page}...")
#             current_url = driver.current_url
            
#             # Wait for the companies to load
#             retry_count = 0
#             if page % 4 == 0:
#                 print("♻️ Restarting browser session to prevent timeout...")
#                 driver.quit()
#                 time.sleep(10)
#                 driver = create_driver()
#                 login(driver)
#                 driver.get(next_url)
#                 random_delay(5, 7)

#             while retry_count < max_retries:
#                 try:
#                     # Check for session expiry
#                     # if check_login_required(driver):
#                     #     print("Session expired, attempting to login again...")
#                     #     if not login(driver):
#                     #         print("Failed to re-login. Exiting...")
#                     #         return companies_data
#                     #     driver.get(current_url)
#                     #     random_delay(5, 7)
#                     if check_login_required(driver):
#                         print("⚠️ Session expired — performing silent re-login...")
#                         try:
#                             if not login(driver):
#                                 print("Silent re-login failed, forcing cookie reload...")
#                                 driver.delete_all_cookies()
#                                 login(driver)
#                                 save_cookies(driver)
#                             driver.get(current_url)
#                             random_delay(5, 7)
#                         except Exception as e:
#                             print(f"Silent re-login error: {e}")
#                             continue

#                     # Updated selectors based on the actual page structure
#                     # Try multiple selectors to find company cards
#                     company_selectors = [
#                         "div[id^='carrier_']",  # Based on the image showing id="carrier_1281167"
#                         "div[class*='border-gray-300']",  # Based on classes in the image
#                         "div[class*='p-6']",  # Based on padding class
#                         "div[class*='bg-primary-50']",  # Based on background class
#                         "div[class*='md:bg-transparent']",  # Based on responsive background class
#                         "div[class*='relative']",  # Based on position class
#                         "div[class*='overflow-hidden']",  # Based on overflow class
#                         "div[class*='x-list-sponsored-content']",  # Based on content class
#                         "article",  # Fallback to article tags
#                         ".carrier-item",  # Common carrier item class
#                         ".company-item"  # Common company item class
#                     ]
                    
#                     companies = []
#                     for selector in company_selectors:
#                         try:
#                             companies = driver.find_elements(By.CSS_SELECTOR, selector)
#                             if companies:
#                                 print(f"Found {len(companies)} companies using selector: {selector}")
#                                 break
#                         except:
#                             continue
                    
#                     if not companies:
#                         print(f"No companies found on page {page} with any selector")
#                         # Take a screenshot for debugging
#                         driver.save_screenshot(f"no_companies_page_{page}.png")
#                         return companies_data
                        
#                     print(f"Found {len(companies)} companies on page {page}")
                    
#                     for company_index, company in enumerate(companies):
#                         try:
#                             # Get company name - try multiple selectors
#                             name_selectors = [
#                                 "h2[class*='text-lg']",
#                                 "h2",
#                                 "h3",
#                                 "[class*='company-name']",
#                                 "[class*='carrier-name']",
#                                 "strong",
#                                 "b"
#                             ]
                            
#                             name = ""
#                             for name_selector in name_selectors:
#                                 try:
#                                     name_element = company.find_element(By.CSS_SELECTOR, name_selector)
#                                     name = name_element.text.strip()
#                                     if name:
#                                         break
#                                 except:
#                                     continue
                            
#                             if not name:
#                                 print(f"Could not find company name for company {company_index + 1}")
#                                 name = f"Unknown Company {company_index + 1}"
                            
#                             print(f"Processing company {company_index + 1}/{len(companies)}: {name}")
                            
#                             # Extract MC and USDOT numbers - try multiple approaches
#                             mc_number = ""
#                             usdot_number = ""
                            
#                             # Try different selectors for identifiers
#                             identifier_selectors = [
#                                 "div.flex.flex-wrap.items-center.gap-2.mb-2 li",
#                                 "li",
#                                 "span",
#                                 "div[class*='flex'] span",
#                                 "div[class*='gap'] span",
#                                 "[class*='identifier']",
#                                 "[class*='mc-number']",
#                                 "[class*='usdot-number']"
#                             ]
                            
#                             for selector in identifier_selectors:
#                                 try:
#                                     identifiers = company.find_elements(By.CSS_SELECTOR, selector)
#                                     for identifier in identifiers:
#                                         text = identifier.text.strip()
#                                         if "MC" in text and not mc_number:
#                                             mc_number = text
#                                         elif "USDOT" in text and not usdot_number:
#                                             usdot_number = text
                                    
#                                     if mc_number and usdot_number:
#                                         break
#                                 except:
#                                     continue
                            
#                             # If still not found, try to extract from the entire company text
#                             if not mc_number or not usdot_number:
#                                 company_text = company.text
#                                 import re
#                                 mc_match = re.search(r'MC\s*\d+', company_text)
#                                 usdot_match = re.search(r'USDOT\s*\d+', company_text)
                                
#                                 if mc_match and not mc_number:
#                                     mc_number = mc_match.group()
#                                 if usdot_match and not usdot_number:
#                                     usdot_number = usdot_match.group()
                            
#                             print(f"Found identifiers - MC: {mc_number}, USDOT: {usdot_number}")
                            
#                             # Get contact information with improved handling
#                             owner_name, phone, email = get_contact_info(driver, company, wait, company_index, current_url)
                            
#                             companies_data.append({
#                                 'Company Name': name,
#                                 'MC Number': mc_number,
#                                 'USDOT Number': usdot_number,
#                                 'Owner Name': owner_name,
#                                 'Phone': phone,
#                                 'Email': email
#                             })
                            
#                             print(f"Successfully processed company {company_index + 1}/{len(companies)}")
                            
#                             # Save data periodically to avoid loss
#                             if len(companies_data) % 10 == 0:
#                                 df_temp = pd.DataFrame(companies_data)
#                                 df_temp.to_csv('trucking_companies_backup.csv', index=False)
#                                 print(f"Backup saved: {len(companies_data)} companies processed so far")
                            
#                         except Exception as e:
#                             print(f"Error processing company {company_index + 1}: {str(e)}")
#                             # Add error entry to maintain count
#                             companies_data.append({
#                                 'Company Name': f"Error processing company {company_index + 1}",
#                                 'MC Number': "Error",
#                                 'USDOT Number': "Error",
#                                 'Owner Name': "Error",
#                                 'Phone': "Error",
#                                 'Email': "Error"
#                             })
#                             continue
                    
#                     # Handle pagination
#                     try:
#                         print("Looking for next page...")
#                         try:
#                             next_link = WebDriverWait(driver, 10).until(
#                                 EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
#                             )
#                         except TimeoutException:
#                             print("Pagination element not clickable. Trying refresh...")
#                             force_refresh_and_relogin(driver, current_url)
#                             continue

#                         if not next_link.is_enabled():
#                             print("Next button is disabled, reached last page")
#                             return companies_data
                        
#                         # Get the next page URL
#                         next_url = next_link.get_attribute('href')
#                         if not next_url or next_url == current_url:
#                             print("No valid next page URL found")
#                             return companies_data
                            
#                         print(f"Moving to page {page + 1}")
                        
#                         # Navigate to next page
#                         driver.get(next_url)
#                         page += 1
#                         random_delay(3, 5)
#                         break  # Break the retry loop on success
                        
#                     except TimeoutException:
#                         print("No next page link found - reached end of pagination")
#                         return companies_data
#                     except Exception as e:
#                         print(f"Error with pagination: {str(e)}")
#                         return companies_data
                        
#                 except TimeoutException:
#                     print(f"Timeout on attempt {retry_count + 1} of {max_retries}")
#                     if retry_count == max_retries - 1:  # If this was our last retry
#                         print(f"Failed to load page {page} after {max_retries} attempts")
#                         return companies_data
#                     retry_count += 1
                    
#                     # Force refresh on timeout
#                     if not force_refresh_and_relogin(driver, current_url):
#                         print("Failed to recover from timeout")
#                         return companies_data
#                     continue
                    
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         if hasattr(driver, 'save_screenshot'):
#             driver.save_screenshot("error.png")
#     finally:
#         try:
#             driver.quit()
#         except:
#             pass
        
#     return companies_data

# def main():
#     url = "https://www.carriersource.io/trucking-companies/flatbed"
    
#     print("Starting the scraping process...")
#     companies_data = scrape_company_data(url)
    
#     # Save to CSV
#     if companies_data:
#         df = pd.DataFrame(companies_data)
#         df.to_csv('trucking_companies.csv', index=False)
#         print(f"Successfully scraped {len(companies_data)} companies. Data saved to trucking_companies.csv")
        
#         # Also save a clean version without error entries
#         clean_data = [entry for entry in companies_data if not any('Error' in str(value) for value in entry.values())]
#         if clean_data:
#             df_clean = pd.DataFrame(clean_data)
#             df_clean.to_csv('trucking_companies_clean.csv', index=False)
#             print(f"Clean data with {len(clean_data)} valid companies saved to trucking_companies_clean.csv")
#     else:
#         print("No data was scraped.")
def scrape_company_data(url, start_page=1, pages_to_scrape=3):
    driver = create_driver()
    if not driver:
        print("Failed to create driver. Exiting...")
        return []
        
    companies_data = []
    page = start_page
    end_page = start_page + pages_to_scrape - 1  # stop after 3 pages
    max_retries = 3
    
    try:
        # Login first
        if not login(driver):
            print("Failed to log in. Exiting...")
            return companies_data
        save_cookies(driver)
    
        # Navigate to the flatbed trucking companies page
        print(f"Navigating to flatbed trucking companies page (starting from page {start_page})...")
        driver.get(f"{url}?page={start_page}")
        random_delay(5, 7)
        
        wait = WebDriverWait(driver, 30)
        
        if not verify_page_loaded(driver, wait):
            print("Page verification failed - trying to reload...")
            if not login(driver):
                print("Failed to re-login. Exiting...")
                return companies_data
            driver.get(f"{url}?page={start_page}")
            random_delay(5, 7)
            if not verify_page_loaded(driver, wait):
                print("Failed to load flatbed trucking companies page after retry")
                return companies_data
        
        print("Successfully verified flatbed trucking companies page loaded")
            
        while True:
            print(f"Scraping page {page}...")
            current_url = driver.current_url

            retry_count = 0
            # if page % 4 == 0:
            #     print("♻️ Restarting browser session to prevent timeout...")
            #     driver.quit()
            #     time.sleep(10)
            #     driver = create_driver()
            #     login(driver)
            #     driver.get(next_url)
            #     random_delay(5, 7)

            while retry_count < max_retries:
                try:
                    if check_login_required(driver):
                        print("⚠️ Session expired — performing silent re-login...")
                        try:
                            if not login(driver):
                                print("Silent re-login failed, forcing cookie reload...")
                                driver.delete_all_cookies()
                                login(driver)
                                save_cookies(driver)
                            driver.get(current_url)
                            random_delay(5, 7)
                        except Exception as e:
                            print(f"Silent re-login error: {e}")
                            continue

                    # --- your scraping logic (selectors, extraction, etc.) remains exactly the same ---
                    company_selectors = [
                        "div[id^='carrier_']",
                        "div[class*='border-gray-300']",
                        "div[class*='p-6']",
                        "div[class*='bg-primary-50']",
                        "div[class*='md:bg-transparent']",
                        "div[class*='relative']",
                        "div[class*='overflow-hidden']",
                        "div[class*='x-list-sponsored-content']",
                        "article",
                        ".carrier-item",
                        ".company-item"
                    ]
                    
                    companies = []
                    for selector in company_selectors:
                        try:
                            companies = driver.find_elements(By.CSS_SELECTOR, selector)
                            if companies:
                                print(f"Found {len(companies)} companies using selector: {selector}")
                                break
                        except:
                            continue
                    
                    if not companies:
                        print(f"No companies found on page {page} with any selector")
                        driver.save_screenshot(f"no_companies_page_{page}.png")
                        return companies_data
                    
                    print(f"Found {len(companies)} companies on page {page}")

                    for company_index, company in enumerate(companies):
                        try:
                            # --- your name/identifier/contact scraping logic stays here unchanged ---
                            name_selectors = [
                                "h2[class*='text-lg']",
                                "h2",
                                "h3",
                                "[class*='company-name']",
                                "[class*='carrier-name']",
                                "strong",
                                "b"
                            ]
                            
                            name = ""
                            for name_selector in name_selectors:
                                try:
                                    name_element = company.find_element(By.CSS_SELECTOR, name_selector)
                                    name = name_element.text.strip()
                                    if name:
                                        break
                                except:
                                    continue
                            
                            if not name:
                                print(f"Could not find company name for company {company_index + 1}")
                                name = f"Unknown Company {company_index + 1}"
                            
                            print(f"Processing company {company_index + 1}/{len(companies)}: {name}")
                            
                            mc_number = ""
                            usdot_number = ""
                            identifier_selectors = [
                                "div.flex.flex-wrap.items-center.gap-2.mb-2 li",
                                "li",
                                "span",
                                "div[class*='flex'] span",
                                "div[class*='gap'] span",
                                "[class*='identifier']",
                                "[class*='mc-number']",
                                "[class*='usdot-number']"
                            ]
                            
                            for selector in identifier_selectors:
                                try:
                                    identifiers = company.find_elements(By.CSS_SELECTOR, selector)
                                    for identifier in identifiers:
                                        text = identifier.text.strip()
                                        if "MC" in text and not mc_number:
                                            mc_number = text
                                        elif "USDOT" in text and not usdot_number:
                                            usdot_number = text
                                    
                                    if mc_number and usdot_number:
                                        break
                                except:
                                    continue
                            
                            if not mc_number or not usdot_number:
                                company_text = company.text
                                import re
                                mc_match = re.search(r'MC\s*\d+', company_text)
                                usdot_match = re.search(r'USDOT\s*\d+', company_text)
                                
                                if mc_match and not mc_number:
                                    mc_number = mc_match.group()
                                if usdot_match and not usdot_number:
                                    usdot_number = usdot_match.group()
                            
                            print(f"Found identifiers - MC: {mc_number}, USDOT: {usdot_number}")
                            
                            owner_name, phone, email = get_contact_info(driver, company, wait, company_index, current_url)
                            
                            companies_data.append({
                                'Company Name': name,
                                'MC Number': mc_number,
                                'USDOT Number': usdot_number,
                                'Owner Name': owner_name,
                                'Phone': phone,
                                'Email': email
                            })
                            
                            print(f"Successfully processed company {company_index + 1}/{len(companies)}")
                            
                            if len(companies_data) % 10 == 0:
                                df_temp = pd.DataFrame(companies_data)
                                df_temp.to_csv('trucking_companies_backup.csv', index=False)
                                print(f"Backup saved: {len(companies_data)} companies processed so far")
                            
                        except Exception as e:
                            print(f"Error processing company {company_index + 1}: {str(e)}")
                            companies_data.append({
                                'Company Name': f"Error processing company {company_index + 1}",
                                'MC Number': "Error",
                                'USDOT Number': "Error",
                                'Owner Name': "Error",
                                'Phone': "Error",
                                'Email': "Error"
                            })
                            continue

                    # Pagination handling
                    print("Looking for next page...")
                    try:
                        next_link = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[rel='next']"))
                        )

                        if not next_link.is_enabled():
                            print("Next button is disabled, reached last page")
                            return companies_data
                        
                        next_url = next_link.get_attribute('href')
                        if not next_url or next_url == current_url:
                            print("No valid next page URL found")
                            return companies_data

                        # ✅ Stop condition: break after scraping 3 pages
                        if page >= start_page + 2:
                            print(f"✅ Reached 3 pages limit (page {page}). Returning data for this batch.")
                            return companies_data

                        print(f"Moving to page {page + 1}")
                        driver.get(next_url)
                        page += 1
                        random_delay(3, 5)
                        break  # Break retry loop after successful navigation

                    except TimeoutException:
                        print("No next page link found - reached end of pagination")
                        return companies_data
                    except Exception as e:
                        print(f"Error with pagination: {str(e)}")
                        return companies_data
                        
                except TimeoutException:
                    print(f"Timeout on attempt {retry_count + 1} of {max_retries}")
                    if retry_count == max_retries - 1:
                        print(f"Failed to load page {page} after {max_retries} attempts")
                        return companies_data
                    retry_count += 1
                    if not force_refresh_and_relogin(driver, current_url):
                        print("Failed to recover from timeout")
                        return companies_data
                    continue

            if page >= end_page:
                print(f"Reached end of batch ({start_page}–{end_page}). Returning data...")
                break
            # -----------------------------------------

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if hasattr(driver, 'save_screenshot'):
            driver.save_screenshot("error.png")
    finally:
        try:
            driver.quit()
            print(f"Closed browser for batch {start_page}–{end_page}")
        except:
            pass
        
    return companies_data
import urllib.parse
from typing import Any, Dict, List, Optional

def build_carriersource_url(
    *,
    company_name: Optional[str] = None,
    fleet_min: Optional[str] = None,
    fleet_max: Optional[str] = None,
    company_type: Optional[str] = None,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    truck_type: Optional[List[str] | str] = None,
    shipment_type: Optional[List[str] | str] = None,
    specialized_service: Optional[List[str] | str] = None,
    freight: Optional[List[str] | str] = None,
    safety_rating: Optional[List[str] | str] = None,
    operation: Optional[List[str] | str] = None,
    insurance_minimum: Optional[str] = None,
    authority_maintained: Optional[str] = None,
) -> str:
    """Construct CarrierSource search URL from given filters.

    Accepts single values or lists for multi-select fields and encodes them
    using repeated query params compatible with urllib.parse.urlencode(doseq=True).
    """
    base_url = "https://www.carriersource.io/trucking-companies/search"

    params: Dict[str, Any] = {
        "carrier[sort]": "cs_score",
    }

    if company_name:
        params["carrier[query]"] = company_name
    if fleet_min:
        params["carrier[fleet_size_min]"] = fleet_min
    if fleet_max:
        params["carrier[fleet_size_max]"] = fleet_max
    if company_type:
        params["carrier[company_type]"] = company_type
    if origin:
        params["carrier[origin]"] = origin
    if destination:
        params["carrier[destination]"] = destination

    # Normalize potential list fields to lists for doseq encoding
    def ensure_list(value: Optional[List[str] | str]) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [v for v in value if v]
        if isinstance(value, str) and value.strip():
            return [value]
        return None

    tt = ensure_list(truck_type)
    st = ensure_list(shipment_type)
    ss = ensure_list(specialized_service)
    fr = ensure_list(freight)
    sr = ensure_list(safety_rating)
    op = ensure_list(operation)

    if tt:
        params["carrier[truck_type]"] = tt
    if st:
        params["carrier[shipment_type]"] = st
    if ss:
        params["carrier[specialized_service]"] = ss
    if fr:
        params["carrier[freight]"] = fr
    if sr:
        params["carrier[safety_rating]"] = sr
    if op:
        params["carrier[operation]"] = op
    if insurance_minimum:
        params["carrier[insurance_minimum]"] = insurance_minimum
    if authority_maintained:
        params["carrier[authority_maintained]"] = authority_maintained

    query_string = urllib.parse.urlencode(params, doseq=True)
    return f"{base_url}?{query_string}" if query_string else base_url

def generate_url():
    """
    Dynamically build CarrierSource search URL based on user filters.
    If no filters are provided, defaults to the base URL.
    """

    base_url = "https://www.carriersource.io/trucking-companies/search"

    print("\nEnter your filters (press Enter to skip any):")

    # Lane search (origin/destination)
    origin = input("Origin (City, State): ").strip()
    destination = input("Destination (City, State): ").strip()

    # Company type (carrier / brokerage)
    company_type = input("Company Type (Carrier / Brokerage): ").strip().lower()

    # Company name
    company_name = input("Company Name (optional): ").strip()

    # Truck type
    truck_type = input("Truck Type (e.g., Dry Van, Reefer, Flatbed): ").strip()

    # Shipment type
    shipment_type = input("Shipment Type (e.g., Full Truckload, LTL): ").strip()

    # Safety rating
    safety_rating = input("Safety Rating (Satisfactory / Conditional / Unsatisfactory / None): ").strip()

    # Operation
    operation = input("Operation (Interstate / Intrastate): ").strip()

    # Fleet size range
    fleet_min = input("Fleet Size Minimum: ").strip()
    fleet_max = input("Fleet Size Maximum: ").strip()

    # Build query parameters dynamically
    params = {
        "carrier[query]": company_name or "",
        "carrier[fleet_size_min]": fleet_min or "",
        "carrier[fleet_size_max]": fleet_max or "",
        "carrier[sort]": "cs_score",  # always include
    }

    # Add filters if present
    if company_type:
        params["carrier[company_type]"] = company_type
    if origin:
        params["carrier[origin]"] = origin
    if destination:
        params["carrier[destination]"] = destination
    if truck_type:
        params["carrier[truck_type]"] = truck_type
    if shipment_type:
        params["carrier[shipment_type]"] = shipment_type
    if safety_rating:
        params["carrier[safety_rating]"] = safety_rating
    if operation:
        params["carrier[operation]"] = operation

    # Encode params into a valid URL
    query_string = urllib.parse.urlencode(params, doseq=True)
    final_url = f"{base_url}?{query_string}"

    print(f"\n✅ Generated URL:\n{final_url}\n")
    return final_url

def run_batched_scrape(url: str, total_pages: int = 30, batch_size: int = 3):
    """Run the batched scraping flow using the provided CarrierSource URL.

    Returns the aggregated list of company dictionaries.
    """
    print(" Starting batched scraping — new browser for each batch...\n")
    all_companies = []
    for start_page in range(1, total_pages + 1, batch_size):
        print(f"Batch: pages {start_page}–{start_page + batch_size - 1}")
        batch_data = scrape_company_data(url, start_page=start_page, pages_to_scrape=batch_size)
        all_companies.extend(batch_data)
        print(
            f"Finished batch {start_page}–{start_page + batch_size - 1}, total collected so far: {len(all_companies)}"
        )
        time.sleep(10)
    return all_companies

def main():
    total_pages = 30
    batch_size = 3
    url = generate_url()
    all_companies = run_batched_scrape(url, total_pages=total_pages, batch_size=batch_size)

    if all_companies:
        df = pd.DataFrame(all_companies)
        df.to_csv("trucking_companies.csv", index=False)
        print(f"\n Saved {len(all_companies)} companies to trucking_companies.csv")

        clean_data = [
            row for row in all_companies
            if not any("Error" in str(v) for v in row.values())
        ]
        if clean_data:
            pd.DataFrame(clean_data).to_csv("trucking_companies_clean.csv", index=False)
            print(f" Clean data ({len(clean_data)} valid companies) saved to trucking_companies_clean.csv")
    else:
        print(" No data was scraped.")



if __name__ == "__main__":
    main()
