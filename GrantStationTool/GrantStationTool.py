import tkinter as tk
from tkinter import ttk
import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import time
import re

class SearchInterface:
    def __init__(self, callback):
        self.callback = callback
        self.root = tk.Tk()
        self.root.title("GrantStation Search")
        self.root.geometry("600x400")
        self.setup_ui()

    def setup_ui(self):
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(
            main_frame, 
            text="GrantStation Search Tool", 
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=20)

        # Search frame
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=20)

        # Search label
        search_label = ttk.Label(
            search_frame, 
            text="Enter search keyword or phrase:",
            font=('Helvetica', 10)
        )
        search_label.pack(pady=(0, 5))

        # Search entry
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(pady=5)
        
        # Add debug checkbox
        self.debug_var = tk.BooleanVar()
        debug_checkbox = ttk.Checkbutton(
            search_frame,
            text="Show Debug Information",
            variable=self.debug_var
        )
        debug_checkbox.pack(pady=5)
        
        # Bind Enter key to search function
        self.search_entry.bind('<Return>', lambda e: self.perform_search())

        # Search button
        search_button = ttk.Button(
            search_frame,
            text="Search",
            command=self.perform_search
        )
        search_button.pack(pady=10)

        # Status label
        self.status_label = ttk.Label(
            main_frame,
            text="",
            font=('Helvetica', 9, 'italic')
        )
        self.status_label.pack(pady=10)

    def perform_search(self):
        search_term = self.search_entry.get().strip()
        if search_term:
            encoded_term = urllib.parse.quote(search_term)
            url = f"https://grantstation.com/search/us-federal?keyword={encoded_term}&opp_number=&cfda="
            
            self.status_label.config(text="Starting search...")
            self.root.update()
            
            # Pass both URL and debug flag to callback
            self.callback([url], self.debug_var.get())
            self.root.destroy()
        else:
            self.status_label.config(text="Please enter a search term")

    def run(self):
        self.root.mainloop()

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
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=self.chrome_options)
        
        # Add undetected-chromedriver properties
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        self.wait = WebDriverWait(self.driver, 20)
        
        # First visit the homepage to get initial cookies
        print("Visiting homepage...")
        self.driver.get("https://grantstation.com")
        time.sleep(3)
        
        # Now visit login page
        print("Accessing login page...")
        self.driver.get("https://grantstation.com/user/login")
        
        try:
            print("Attempting enhanced login...")
            # Wait for form to be interactive
            self.wait.until(EC.presence_of_element_located((By.ID, "user-login-form")))
            self.wait.until(EC.element_to_be_clickable((By.ID, "edit-name")))
            
            # Get all form tokens
            form = self.driver.find_element(By.ID, "user-login-form")
            form_build_id = form.find_element(By.CSS_SELECTOR, 'input[name="form_build_id"]').get_attribute('value')
            form_id = form.find_element(By.CSS_SELECTOR, 'input[name="form_id"]').get_attribute('value')
            
            print("Entering credentials...")
            # Enter credentials with delays to mimic human behavior
            username_field = form.find_element(By.ID, 'edit-name')
            self.type_with_delay(username_field, self.username)
            
            password_field = form.find_element(By.ID, 'edit-pass')
            self.type_with_delay(password_field, self.password)
            
            # Submit form using JavaScript
            print("Submitting form...")
            self.driver.execute_script("""
                document.getElementById('edit-submit').click();
            """)
            
            # Wait for redirect and verify login
            time.sleep(5)
            print(f"Current URL after login attempt: {self.driver.current_url}")
            
            # Check if login was successful
            if "user/login" in self.driver.current_url.lower():
                print("Login may have failed. Attempting alternative login method...")
                self.attempt_alternative_login()
            else:
                print("Login appears successful")
                
        except Exception as e:
            print(f"Error during login: {str(e)}")
            self.results_text += f"\nError during login: {str(e)}\n"

    def attempt_alternative_login(self):
        """Alternative login method using direct POST request"""
        try:
            # Get the current cookies
            cookies = self.driver.get_cookies()
            session = requests.Session()
            
            # Add cookies to session
            for cookie in cookies:
                session.cookies.set(cookie['name'], cookie['value'])
            
            # Get form tokens
            response = session.get("https://grantstation.com/user/login")
            
            # Extract form tokens from response
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
                
                # Attempt login
                login_response = session.post(
                    "https://grantstation.com/user/login",
                    data=login_data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                # If successful, transfer session cookies to selenium
                if login_response.status_code == 200:
                    for cookie in session.cookies:
                        self.driver.add_cookie({
                            'name': cookie.name,
                            'value': cookie.value,
                            'domain': cookie.domain
                        })
                    
                    # Refresh page to apply new cookies
                    self.driver.refresh()
                    time.sleep(3)
            
        except Exception as e:
            print(f"Alternative login failed: {str(e)}")

    def save_cookies(self):
        """Save cookies to a file"""
        if self.driver:
            cookies = self.driver.get_cookies()
            with open('grantstation_cookies.json', 'w') as f:
                json.dump(cookies, f)
            print("Cookies saved successfully")

    def load_cookies(self):
        """Load cookies from file if they exist"""
        try:
            with open('grantstation_cookies.json', 'r') as f:
                cookies = json.load(f)
                # First visit the site to be able to add cookies
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

    def type_with_delay(self, element, text):
        """Type text with random delays to mimic human behavior"""
        for character in text:
            element.send_keys(character)
            time.sleep(0.1)

    def extract_grant_info(self, url):
        try:
            print(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            # Get page source
            page_source = self.driver.page_source
            
            # Try multiple methods to extract data
            data = []
            
            # Method 1: Direct Selenium extraction
            try:
                rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody > tr")
                for row in rows:
                    item = self.extract_row_data(row)
                    if item:
                        data.append(item)
            except Exception as e:
                print(f"Selenium extraction failed: {str(e)}")
            
            # Method 2: Parse HTML directly if needed
            if not data:
                print("Attempting direct HTML parsing...")
                pattern = r'<tr[^>]*>.*?<td[^>]*>.*?title">(.*?)</td>.*?agency-name">(.*?)</td>.*?post-date">(.*?)</td>.*?close-date">(.*?)</td>'
                matches = re.finditer(pattern, page_source, re.DOTALL)
                for match in matches:
                    data.append({
                        'title': match.group(1).strip(),
                        'agency': match.group(2).strip(),
                        'post_date': match.group(3).strip(),
                        'close_date': match.group(4).strip()
                    })
            
            return data
            
        except Exception as e:
            print(f"Error extracting data: {str(e)}")
            return []

    def extract_grant_info(self, url):
        """Extract grant information including detailed pages"""
        try:
            print(f"Accessing URL: {url}")
            self.driver.get(url)
            time.sleep(5)  # Allow page to load completely
            
            # First get all opportunity links from the search results page
            opportunity_links = self.extract_opportunity_links(self.driver.page_source)
            
            detailed_results = []
            for link in opportunity_links:
                try:
                    detailed_info = self.extract_detailed_info(link['url'])
                    if detailed_info:
                        detailed_results.append(detailed_info)
                        # Add some spacing between opportunities in the results text
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

    def extract_opportunity_links(self, main_page_source):
        """Extract all opportunity links from the search results page"""
        links = []
        try:
            # Find all opportunity title links
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
        """Extract detailed information from an opportunity's page"""
        try:
            print(f"Accessing detailed page: {url}")
            self.driver.get(url)
            time.sleep(3)  # Allow page to load

            # Try multiple methods to get the title
            title = (
                self.safe_get_text_by_selector("h1.page-header") or 
                self.safe_get_text_by_selector("meta[property='og:title']", attribute='content') or
                self.safe_get_text_by_selector("div.views-field-title") or
                "Title Not Found"
            )

            # Add debug information
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
        """Safely get text content using CSS selector"""
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
        """Safely get link href using CSS selector"""
        try:
            element = self.driver.find_element(By.CSS_SELECTOR, selector)
            return element.get_attribute('href')
        except:
            return None

    def get_eligible_applicants(self):
        """Extract list of eligible applicants"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div#elig-app-in-profile .field__item")
            return [elem.text.strip() for elem in elements]
        except:
            return []

    def get_cfda_numbers(self):
        """Extract CFDA numbers"""
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, "div#cfda-numbers-in-profile .field__item")
            return [elem.text.strip() for elem in elements]
        except:
            return []

    def try_multiple_selectors(self, element, selectors):
        for selector in selectors:
            try:
                return element.find_element(By.CSS_SELECTOR, selector).text.strip()
            except:
                continue
        return "N/A"

    def display_results(self):
        """Display results in a tkinter window"""
        results_window = tk.Tk()
        results_window.title("GrantStation Search Results")
        
        # Configure the window
        results_window.geometry("1000x800")
        
        # Create main frame with padding
        main_frame = ttk.Frame(results_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Add notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Results tab
        results_frame = ttk.Frame(notebook)
        notebook.add(results_frame, text="Results")

        # Debug tab (if debug mode is on)
        if self.debug_mode:
            debug_frame = ttk.Frame(notebook)
            notebook.add(debug_frame, text="Debug Info")
            
            debug_text = tk.Text(debug_frame, wrap="word")
            debug_scrollbar = ttk.Scrollbar(debug_frame)
            
            debug_scrollbar.pack(side="right", fill="y")
            debug_text.pack(side="left", expand=True, fill="both")
            
            debug_text.insert("1.0", self.debug_text)
            debug_scrollbar.config(command=debug_text.yview)
            debug_text.config(yscrollcommand=debug_scrollbar.set)

        # Results text widget
        results_text = tk.Text(results_frame, wrap="word")
        results_scrollbar = ttk.Scrollbar(results_frame)
        
        results_scrollbar.pack(side="right", fill="y")
        results_text.pack(side="left", expand=True, fill="both")
        
        results_text.insert("1.0", self.results_text)
        results_scrollbar.config(command=results_text.yview)
        results_text.config(yscrollcommand=results_scrollbar.set)

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        save_results_button = ttk.Button(
            button_frame, 
            text="Save Results", 
            command=self.save_results
        )
        save_results_button.pack(side="left", padx=5)
        
        new_search_button = ttk.Button(
            button_frame,
            text="New Search",
            command=lambda: self.start_new_search(results_window)
        )
        new_search_button.pack(side="left", padx=5)
        
        results_window.mainloop()

    def run(self, urls, debug_mode=False):
        """Main method to run the scraper"""
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
            
            self.display_results()
            
        finally:
            if self.driver:
                self.driver.quit()
    def save_results(self):
        filename = "grantstation_results.txt"
        with open(filename, "w", encoding='utf-8') as f:
            f.write(self.results_text)
        print(f"Results saved to {filename}")

    def start_new_search(self, current_window):
        current_window.destroy()
        self.results_text = ""
        if self.driver:
            self.driver.quit()
        start_search(self.username, self.password)

def start_search(username, password):
    """Initialize the search interface and scraper"""
    scraper = GrantStationScraper(username, password)
    search_ui = SearchInterface(scraper.run)
    search_ui.run()

if __name__ == "__main__":
    username = 'wayne.geffen@gmail.com'
    password = 'dsala2024####'
    
    print("Starting GrantStation search tool...")
    start_search(username, password)