import undetected_chromedriver as uc
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

# Login credentials
EMAIL = "jacob@sfsolutions-usa.com"
PASSWORD = "Omnamahshiv@123"
LOGIN_URL = "https://carriersource.io/login"

def create_driver():
    """Create and return an undetected Chrome instance"""
    try:
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Create the driver with a longer timeout
        driver = uc.Chrome(
            options=options,
            driver_executable_path=None,
            browser_executable_path=None,
            suppress_welcome=True,
            use_subprocess=True
        )
        
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

def handle_recaptcha(driver, wait):
    """Handle reCAPTCHA with human-like behavior"""
    try:
        print("Looking for reCAPTCHA...")
        
        # Wait for all iframes to be present
        time.sleep(2)  # Give extra time for iframes to load
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        # Find the reCAPTCHA iframe
        recaptcha_iframe = None
        for iframe in iframes:
            try:
                if 'recaptcha' in iframe.get_attribute('src').lower():
                    recaptcha_iframe = iframe
                    break
            except:
                continue
        
        if not recaptcha_iframe:
            print("No reCAPTCHA iframe found, proceeding anyway...")
            return True
            
        print("Found reCAPTCHA iframe")
        
        # Switch to the iframe
        driver.switch_to.frame(recaptcha_iframe)
        
        # Wait for and find the checkbox
        try:
            checkbox = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".recaptcha-checkbox-border")))
            checkbox.click()
            print("Clicked reCAPTCHA checkbox")
        except:
            print("Couldn't find or click reCAPTCHA checkbox")
        
        # Switch back to main content
        driver.switch_to.default_content()
        
        # Wait a bit for any additional challenges
        time.sleep(3)
        
        return True
    except Exception as e:
        print(f"reCAPTCHA handling error: {str(e)}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return True  # Continue anyway

def login(driver):
    """Handle the login process"""
    try:
        print("Attempting to log in...")
        driver.get(LOGIN_URL)
        random_delay(3, 5)  # Increased initial delay for page load
        
        wait = WebDriverWait(driver, 20)  # Increased wait time
        
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
        random_delay(5, 7)  # Increased delay after login attempt
        
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
                            companies = wait.until(EC.presence_of_all_elements_located((
                                By.CSS_SELECTOR, 
                                "div[itemtype='https://schema.org/LocalBusiness']"
                            )))
                            
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
                    companies = wait.until(EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, 
                        "div[itemtype='https://schema.org/LocalBusiness']"
                    )))
                    
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
                companies = wait.until(EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 
                    "div[itemtype='https://schema.org/LocalBusiness']"
                )))
                
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
                print(f"No modal found for {company_name}")
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
                companies = wait.until(EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR, 
                    "div[itemtype='https://schema.org/LocalBusiness']"
                )))
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

def scrape_company_data(url):
    driver = create_driver()
    if not driver:
        print("Failed to create driver. Exiting...")
        return []
        
    companies_data = []
    page = 1
    max_retries = 3
    
    try:
        # Login first
        if not login(driver):
            print("Failed to log in. Exiting...")
            return companies_data
            
        # Navigate to the flatbed trucking companies page
        print("Navigating to flatbed trucking companies page...")
        driver.get(url)
        random_delay(5, 7)  # Give enough time for the page to load
        
        wait = WebDriverWait(driver, 30)
        
        # Verify we're on the correct page by checking for carrier listings
        try:
            wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, 
                "div[itemtype='https://schema.org/LocalBusiness']"
            )))
            print("Successfully loaded flatbed trucking companies page")
        except TimeoutException:
            print("Failed to load flatbed trucking companies page")
            if hasattr(driver, 'save_screenshot'):
                driver.save_screenshot("page_load_failed.png")
            return companies_data
            
        while True:
            print(f"Scraping page {page}...")
            current_url = driver.current_url
            
            # Wait for the companies to load
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # Check for session expiry
                    if check_login_required(driver):
                        print("Session expired, attempting to login again...")
                        if not login(driver):
                            print("Failed to re-login. Exiting...")
                            return companies_data
                        driver.get(current_url)
                        random_delay(5, 7)
                    
                    # Updated selector for company elements
                    companies = wait.until(EC.presence_of_all_elements_located((
                        By.CSS_SELECTOR, 
                        "div[itemtype='https://schema.org/LocalBusiness']"
                    )))
                    
                    if not companies:
                        print(f"No companies found on page {page}")
                        return companies_data
                        
                    print(f"Found {len(companies)} companies on page {page}")
                    
                    for company_index, company in enumerate(companies):
                        try:
                            # Get company name
                            try:
                                name = company.find_element(
                                    By.CSS_SELECTOR, 
                                    "h2[class*='text-lg']"
                                ).text.strip()
                            except:
                                print("Failed to find company name with primary selector, trying backup...")
                                name = company.find_element(By.TAG_NAME, "h2").text.strip()
                            
                            print(f"Processing company {company_index + 1}/{len(companies)}: {name}")
                            
                            # Extract MC and USDOT numbers
                            identifiers = company.find_elements(
                                By.CSS_SELECTOR, 
                                "div.flex.flex-wrap.items-center.gap-2.mb-2 li"
                            )
                                
                            mc_number = ""
                            usdot_number = ""
                            
                            for identifier in identifiers:
                                text = identifier.text.strip()
                                if "MC" in text:
                                    mc_number = text
                                elif "USDOT" in text:
                                    usdot_number = text
                            
                            print(f"Found identifiers - MC: {mc_number}, USDOT: {usdot_number}")
                            
                            # Get contact information with improved handling
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
                            
                            # Save data periodically to avoid loss
                            if len(companies_data) % 10 == 0:
                                df_temp = pd.DataFrame(companies_data)
                                df_temp.to_csv('trucking_companies_backup.csv', index=False)
                                print(f"Backup saved: {len(companies_data)} companies processed so far")
                            
                        except Exception as e:
                            print(f"Error processing company {company_index + 1}: {str(e)}")
                            # Add error entry to maintain count
                            companies_data.append({
                                'Company Name': f"Error processing company {company_index + 1}",
                                'MC Number': "Error",
                                'USDOT Number': "Error",
                                'Owner Name': "Error",
                                'Phone': "Error",
                                'Email': "Error"
                            })
                            continue
                    
                    # Handle pagination
                    try:
                        print("Looking for next page...")
                        next_link = wait.until(EC.presence_of_element_located((
                            By.CSS_SELECTOR, 
                            "a[rel='next']"
                        )))
                        
                        if not next_link.is_enabled():
                            print("Next button is disabled, reached last page")
                            return companies_data
                        
                        # Get the next page URL
                        next_url = next_link.get_attribute('href')
                        if not next_url or next_url == current_url:
                            print("No valid next page URL found")
                            return companies_data
                            
                        print(f"Moving to page {page + 1}")
                        
                        # Navigate to next page
                        driver.get(next_url)
                        page += 1
                        random_delay(3, 5)
                        break  # Break the retry loop on success
                        
                    except TimeoutException:
                        print("No next page link found - reached end of pagination")
                        return companies_data
                    except Exception as e:
                        print(f"Error with pagination: {str(e)}")
                        return companies_data
                        
                except TimeoutException:
                    print(f"Timeout on attempt {retry_count + 1} of {max_retries}")
                    if retry_count == max_retries - 1:  # If this was our last retry
                        print(f"Failed to load page {page} after {max_retries} attempts")
                        return companies_data
                    retry_count += 1
                    
                    # Force refresh on timeout
                    if not force_refresh_and_relogin(driver, current_url):
                        print("Failed to recover from timeout")
                        return companies_data
                    continue
                    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        if hasattr(driver, 'save_screenshot'):
            driver.save_screenshot("error.png")
    finally:
        try:
            driver.quit()
        except:
            pass
        
    return companies_data

def main(custom_url=None):
    url = custom_url or "https://www.carriersource.io/trucking-companies/flatbed"
    print(f"Starting the scraping process for URL: {url}")
    companies_data = scrape_company_data(url)
    
    # Save to CSV
    if companies_data:
        df = pd.DataFrame(companies_data)
        output_file = 'trucking_companies.csv'
        df.to_csv(output_file, index=False)
        print(f"Successfully scraped {len(companies_data)} companies. Data saved to {output_file}")
        
        # Also save a clean version without error entries
        clean_data = [entry for entry in companies_data if not any('Error' in str(value) for value in entry.values())]
        if clean_data:
            clean_file = 'trucking_companies_clean.csv'
            df_clean = pd.DataFrame(clean_data)
            df_clean.to_csv(clean_file, index=False)
            print(f"Clean data with {len(clean_data)} valid companies saved to {clean_file}")
        
        return companies_data
    else:
        print("No data was scraped.")
        return []

if __name__ == "__main__":
    main()