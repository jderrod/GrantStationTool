from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import tkinter as tk
import time

# Initialize the Chrome driver
driver = webdriver.Chrome()

# Create WebDriverWait instance for reuse
wait = WebDriverWait(driver, 20)

# List of URLs to scrape
urls = [
    "https://grantstation.com/search/us-federal?keyword=developmental+disorder&opp_number=&cfda=",
    "https://grantstation.com/search/us-federal?keyword=Mental+Illness&opp_number=&cfda="
]

# Prepare data for display
results_text = ""

for url in urls:
    # Step 1: Navigate directly to the search results page
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    # Step 2: Check if login is required by looking for the login fields
    try:
        # Try to locate the username field on the page, if present
        username_field = wait.until(EC.presence_of_element_located((By.ID, 'edit-name')))
        password_field = driver.find_element(By.ID, 'edit-pass')

        # Login
        print("Login fields found, attempting to log in...")
        username = 'wayne.geffen@gmail.com'  # Replace with your actual username
        password = 'dsala2024####'  # Replace with your actual password

        username_field.send_keys(username)
        password_field.send_keys(password)

        # Locate and click the login button
        login_button = driver.find_element(By.ID, 'edit-submit')  # Assuming 'edit-submit' is the ID of the login button
        login_button.click()

        # Wait for the login to complete and for the main content to load
        wait.until(EC.presence_of_element_located((By.ID, "main-content")))
        print("Logged in successfully.")
    except Exception as e:
        # If no login fields are found, we assume we're already logged in
        print("No login fields found. Assuming already logged in.")

    # Step 3: Wait for the search results to load
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tbody > tr")))

    # Find all rows in the table
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody > tr")

    for index, row in enumerate(rows):
        try:
            # Extract relevant data from each cell
            agency_name = row.find_element(By.CSS_SELECTOR, "td.views-field-field-agency-name").text.strip()
            post_date = row.find_element(By.CSS_SELECTOR, "td.views-field-field-post-date").text.strip()
            close_date = row.find_element(By.CSS_SELECTOR, "td.views-field-field-close-date").text.strip()

            # Attempt to get the opportunity title
            opportunity_title_element = row.find_element(By.CSS_SELECTOR, "td.views-field-title")
            opportunity_title = opportunity_title_element.text.strip()

            # Add data to the results text
            results_text += f"URL: {url}\n"
            results_text += f"Row {index + 1}:\n"
            results_text += f"  Opportunity Title: {opportunity_title}\n"
            results_text += f"  Agency: {agency_name}\n"
            results_text += f"  Post Date: {post_date}\n"
            results_text += f"  Close Date: {close_date}\n\n"

        except Exception as e:
            results_text += f"An error occurred at row {index + 1} for URL {url}: {e}\n"

# Quit the driver at the end
driver.quit()

# Step 4: Display the results in a tkinter window
root = tk.Tk()
root.title("Scraped Results")

# Create a text widget to display the results
text_widget = tk.Text(root, wrap="word")
text_widget.insert("1.0", results_text)
text_widget.pack(expand=True, fill="both")

# Add a scrollbar for the text widget
scrollbar = tk.Scrollbar(text_widget)
scrollbar.pack(side="right", fill="y")
scrollbar.config(command=text_widget.yview)
text_widget.config(yscrollcommand=scrollbar.set)

# Run the tkinter main loop
root.mainloop()
