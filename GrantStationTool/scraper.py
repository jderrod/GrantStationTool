# scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from results_window import ResultsWindow
import requests
import json
import time

class GrantStationScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.chrome_options = Options()
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option('useAutomationExtension', False)
        self.driver = None
        self.wait = None
        self.results_text = ""
        self.debug_mode = False
        self.debug_text = ""

    def initialize_driver(self):
        print("Initializing Chrome driver...")
        try:
            # Updated driver initialization with explicit version
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            
            # Get the latest stable Chrome driver
            driver_path = ChromeDriverManager().install()
            print(f"Driver path: {driver_path}")
            
            service = Service(driver_path)
            
            # Add additional Chrome options
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            
            # Create the driver with error handling
            try:
                self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
            except Exception as e:
                print(f"Error creating Chrome driver: {str(e)}")
                # Try alternative initialization
                self.driver = webdriver.Chrome(options=self.chrome_options)
            
            # Add undetected-chromedriver properties
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.wait = WebDriverWait(self.driver, 20)
            
            print("Visiting homepage...")
            self.driver.get("https://grantstation.com")
            time.sleep(3)
            
            print("Accessing login page...")
            self.driver.get("https://grantstation.com/user/login")
            
            # Rest of the initialization code...
            
        except Exception as e:
            print(f"Failed to initialize driver: {str(e)}")
            raise
        
    def type_with_delay(self, element, text):
        for character in text:
            element.send_keys(character)
            time.sleep(0.1)

    def attempt_alternative_login(self):
        try:
            cookies = self.driver.get_cookies()
            session = requests.Session()
            
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            response = session.get("https://grantstation.com/user/login")
            
            form_build_id = re.search(r'name="form_build_id" value="([^"]+)"', response.text)
            form_token = re.search(r'name="form_token" value="([^"]+)"', response.text)
            
            if form_build_id and form_token:
                login_data = {
                    'name': self.username,
                    'pass': self.password,
                    'form_build_id': form_build_id.group(1),
                    'form_token': form_token.group(1),
                    'form_id': 'user_login_form',
                    'op': 'Log in'
                }
                
                login_response = session.post(
                    "https://grantstation.com/user/login",
                    data=login_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                if login_response.status_code == 200:
                    for cookie in session.cookies:
                        self.driver.add_cookie({
                            'name': cookie.name,
                            'value': cookie.value,
                            'domain': cookie.domain
                        })
                    
                    self.driver.refresh()
                    time.sleep(3)
            
        except Exception as e:
            print(f"Alternative login failed: {str(e)}")

    def extract_opportunity_links(self, main_page_source):
        links = []
        try:
            title_elements = self.driver.find_elements(By.CSS_SELECTOR, "td.views-field-title a")
            for element in title_elements:
                href = element.get_attribute('href')
                title = element.text.strip()
                if href:
                    links.append({'url': href, 'title': title})
            return links
        except Exception as e:
            print(f"Error extracting opportunity links: {str(e)}")
            return []

    def extract_detailed_info(self, url):
        try:
            print(f"Accessing detailed page: {url}")
            self.driver.get(url)
            time.sleep(3)

            title = (
                self.safe_get_text_by_selector("h1.page-header") or 
                self.safe_get_text_by_selector("meta[property='og:title']", attribute='content') or
                self.safe_get_text_by_selector("div.views-field-title") or
                "Title Not Found"
            )

            if self.debug_mode:
                self.debug_text += f"\nDEBUG: Extracting from URL: {url}\n"
                self.debug_text += f"DEBUG: Raw title found: {title}\n"

            detailed_info = {
                'title': title,
                'description': self.safe_get_text_by_selector("div.field--name-field-description"),
                'agency': self.safe_get_text_by_selector("div.field--name-field-agency-name"),
                'opportunity_number': self.safe_get_text_by_selector("div.field--name-field-funding-opportunity-number"),
                'post_date': self.safe_get_text_by_selector("div.field--name-field-post-date"),
                'close_date': self.safe_get_text_by_selector("div.field--name-field-close-date"),
                'eligible_applicants': self.get_eligible_applicants(),
                'additional_eligibility': self.safe_get_text_by_selector("div#add-elig-in-profile"),
                'cfda_numbers': self.get_cfda_numbers(),
                'additional_info_url': self.safe_get_link_by_selector("div.field--name-field-additional-information a")
            }

            # Add grants.gov link if present
            grants_gov_link = self.safe_get_link_by_selector("div.visit-website-link a")
            if grants_gov_link:
                detailed_info['grants_gov_url'] = grants_gov_link

            if self.debug_mode:
                self.debug_text += "DEBUG: Extracted fields:\n"
                for key, value in detailed_info.items():
                    self.debug_text += f"DEBUG: {key}: {value}\n"

            return detailed_info

        except Exception as e:
            error_msg = f"Error extracting detailed info: {str(e)}"
            print(error_msg)
            if self.debug_mode:
                self.debug_text += f"DEBUG ERROR: {error_msg}\n"
            return None

    def safe_get_text_by_selector(self, selector, attribute=None):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            if attribute:
                return element.get_attribute(attribute)
            return element.text.strip()
        except Exception as e:
            if self.debug_mode:
                self.debug_text += f"DEBUG: Failed to get text for selector '{selector}': {str(e)}\n"
            return "N/A"

    def safe_get_link_by_selector(self, selector):
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute('href')
        except:
            return None

    def get_eligible_applicants(self):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div#elig-app-in-profile .field__item")
            return [elem.text.strip() for elem in elements]
        except:
            return []

    def get_cfda_numbers(self):
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div#cfda-numbers-in-profile .field__item")
            return [elem.text.strip() for elem in elements]
        except:
            return []

    def save_results(self):
        filename = "grantstation_results.txt"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(self.results_text)
        print(f"Results saved to {filename}")

    def start_new_search(self, current_window):
        """Close current results and start new search"""
        current_window.destroy()
        self.results_text = ""
        if self.driver:
            self.driver.quit()
        from main import start_new_search  # Import here to avoid circular import
        start_new_search()

    def extract_grant_info(self, url):
        try:
            print(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            opportunity_links = self.extract_opportunity_links(self.driver.page_source)
            
            detailed_results = []
            for link in opportunity_links:
                try:
                    detailed_info = self.extract_detailed_info(link['url'])
                    if detailed_info:
                        detailed_results.append(detailed_info)
                        self.results_text += "\n" + "="*50 + "\n"
                        self.results_text += f"Title: {detailed_info['title']}\n"
                        self.results_text += f"Agency: {detailed_info['agency']}\n"
                        self.results_text += f"Opportunity Number: {detailed_info['opportunity_number']}\n"
                        self.results_text += f"Post Date: {detailed_info['post_date']}\n"
                        self.results_text += f"Close Date: {detailed_info['close_date']}\n"
                        self.results_text += f"Description: {detailed_info['description']}\n"
                        self.results_text += "\nEligible Applicants:\n"
                        for applicant in detailed_info['eligible_applicants']:
                            self.results_text += f"- {applicant}\n"
                        self.results_text += f"\nCFDA Numbers: {', '.join(detailed_info['cfda_numbers'])}\n"
                        if detailed_info.get('grants_gov_url'):
                            self.results_text += f"Grants.gov URL: {detailed_info['grants_gov_url']}\n"
                        if detailed_info['additional_info_url']:
                            self.results_text += f"Additional Information: {detailed_info['additional_info_url']}\n"
                except Exception as e:
                    print(f"Error processing opportunity {link['url']}: {str(e)}")
                    
            return detailed_results
            
        except Exception as e:
            print(f"Error extracting data: {str(e)}")
            return []

    def run(self, urls, debug_mode=False):
        try:
            self.debug_mode = debug_mode
            self.initialize_driver()
            
            if self.load_cookies():
                print("Attempting to use saved cookies...")
                self.driver.get("https://grantstation.com")
                time.sleep(3)
                
                if "user/login" in self.driver.current_url.lower():
                    print("Saved cookies expired, logging in again...")
                    self.initialize_driver()
                else:
                    print("Successfully logged in with saved cookies")
            
            for url in urls:
                data = self.extract_grant_info(url)
                self.results_text += f"\nResults for {url}:\n"
                for item in data:
                    self.results_text += json.dumps(item, indent=2) + "\n\n"
            
            results_window = ResultsWindow(
                self.results_text,
                self.debug_text,
                self.debug_mode,
                lambda: self.start_new_search(results_window.window),
                self.save_results
            )
            results_window.display()
            
        finally:
            if self.driver:
                self.driver.quit()

    def load_cookies(self):
        try:
            with open('grantstation_cookies.json', 'r') as f:
                cookies = json.load(f)
                self.driver.get("https://grantstation.com")
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                print("Cookies loaded successfully")
                return True
        except FileNotFoundError:
            print("No saved cookies found")
            return False
        except Exception as e:
            print(f"Error loading cookies: {str(e)}")
            return False

    def save_cookies(self):
        if self.driver:
            cookies = self.driver.get_cookies()
            with open('grantstation_cookies.json', 'w') as f:
                json.dump(cookies, f)
            print("Cookies saved successfully")