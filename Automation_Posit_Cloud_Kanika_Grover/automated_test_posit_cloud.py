import sys
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException 
import time
import logging


# Setting up logging configuration to log to both a file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), 'script.log')),  # Log to a file
        logging.StreamHandler(sys.stdout)   # Also log to the console
    ]
)

# Custom log function that replaces print
def log_message(message):
    logging.info(message)  # Logs to both the console and the file

# Override print with the custom log function
def custom_print(*args, **kwargs):
    message = ' '.join(map(str, args))
    log_message(message)

# Reassign the print function to the custom function
print = custom_print

# Print to console when screenshot is saved
def save_screenshot(driver, file_path):
    if driver.save_screenshot(file_path):
        print(f"Screenshot Captured @ {file_path}")

def print_bold(message):
    print("\033[1m" + message + "\033[0m")

# Setup WebDriver and open Posit Cloud
def setup_driver():
    options = webdriver.ChromeOptions()
    
    # Run Chrome in headless mode
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
    options.add_argument("--disable-gpu")  # Applicable only for Windows environments

    # Browsers supported: https://posit.gac.edu/unsupported_browser.htm
    # Set a supported user agent to avoid browser incompatibility
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")
    print("Homepage loaded")
    driver = webdriver.Chrome(options=options)
    
    # Clear cookies
    driver.delete_all_cookies()

    # Add implicit wait
    driver.implicitly_wait(5)

    # Open the desired URL
    driver.get("https://posit.cloud")
    save_screenshot(driver, "screenshots/setup_driver_loaded.png")
    print("Posit Cloud homepage")
    return driver


# Log in to Posit Cloud
def login(driver, username, password):
    """
    Log in to the Posit Cloud platform using credentials provided at runtime.
    Args:
        driver: WebDriver instance
        username: Username for login
        password: Password for login
    """
    try:
        # Click on the "Log In" button on the top-right
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Log In"))
        )
        login_button.click()
        print("Login button clicked, waiting for login page...")
        
        # Wait for the login page to load
        WebDriverWait(driver, 20).until(EC.url_contains("login.posit.cloud"))
        #print(f"Current URL after clicking Log In: {driver.current_url}")
        save_screenshot(driver, "screenshots/login_click.png")

        # Enter login email
        email_field = driver.find_element(By.XPATH, "//input[@type='email']")
        email_field.click()
        email_field.send_keys(username)
        print("Email entered")
        save_screenshot(driver, "screenshots/email_entered.png")

        # Click the "Continue" button
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        continue_button.click()
        print("Continue button clicked, waiting for password input...")

        # Wait for password page to load
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@type='password']"))
        )
        save_screenshot(driver,"screenshots/continue_clicked.png")

        # Find the password input field and input the password
        password_field = driver.find_element(By.XPATH, "//input[@type='password']")
        password_field.click()
        password_field.send_keys(password)
        print("Password entered")
        save_screenshot(driver,"screenshots/password_entered.png")

        # Click the "Login" button
        login_submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_submit_button.click()
        print("Login submit clicked, waiting for workspace to load...")

        # Wait for workspace to load after successful login
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your Workspace')]")))
        print("Successfully logged into workspace")
        save_screenshot(driver,"screenshots/logged_in.png")

    except Exception as e:
        print(f"Error during login: {str(e)}")
        save_screenshot(driver,"screenshots/login_error.png")
        print("Screenshot saved for login error.")

# Create a new space
def create_space(driver):
    """
    Create a new space within the Posit Cloud platform.
    Args:
        driver: WebDriver instance
    """
    try:

        # Click "New Space" button on the side navpanel
        new_space_button = driver.find_element(By.XPATH, "//span[contains(text(), 'New Space')]")
        driver.execute_script("arguments[0].click();", new_space_button)
        print("New Space button clicked")

        # Wait for the modal dialog to appear
        modal_dialog = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "modalDialog"))
        )
        print("New Space modal is visible")

        # Locate the space name input field and enter space name
        space_name_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.XPATH, "//input[@id='name']"))
        )
        space_name_input.click()
        space_name_input.send_keys("QA_TestSpace")
        print("Space name entered")
        save_screenshot(driver,"screenshots/space_name_entered.png")

        # Click the "Create" button
        create_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        create_button.click()
        print("Create button clicked")

        # Validate if the space was created
        WebDriverWait(driver, 10).until(
           EC.text_to_be_present_in_element((By.ID, "headerTitle"), "QA_TestSpace")
        )
        print("Space creation validated")

        save_screenshot(driver,"screenshots/space_creation_success.png")

    except Exception as e:
        print(f"Error during space creation: {e}")
        save_screenshot(driver,"screenshots/space_creation_error.png")


def create_project_in_space(driver):
    """
    Create a new RStudio project within the created space in Posit Cloud.
    Args:
        driver: WebDriver instance
    """
    try:
        # Click on the "New Project" button
        new_project_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@title, 'New Project')]"))
        )
        driver.execute_script("arguments[0].click();", new_project_button)
        print("New Project button clicked")
        save_screenshot(driver,"screenshots/new_project_clicked.png")

        # Select "New RStudio Project" from the dropdown
        rstudio_project_option = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'New RStudio Project')]"))
        )
        rstudio_project_option.click()
        print("New RStudio Project option selected")

        # Wait for the project deployment to complete
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//span[text()='Deploying Project']"))
        )
        print("Project deployment initiated, waiting for project to deploy...")
        time.sleep(20)  # Wait for project to fully load (can be adjusted between 15-30 sec, manually calculated)
        print("New RStudio Project created in QA_TestSpace")
        save_screenshot(driver,"screenshots/project_created.png")

    except Exception as e:
        print(f"Error during project creation or renaming: {e}")
        save_screenshot(driver,"screenshots/project_creation_error.png")

# Verify that the RStudio IDE loads
def verify_rstudio_ide(driver):
    """
    Verify that the RStudio IDE has successfully loaded within the project.
    Args:
        driver: WebDriver instance
    """
    try:
        time.sleep(5)  # Allow time for the IDE to load
        assert "RStudio" in driver.page_source  # Validate presence of RStudio IDE
        print("RStudio IDE loaded successfully.")
    except Exception as e:
        print("Error verifying RStudio IDE: {}".format(e))

# Main function to execute the full test
def run_test(username, password):
    """
    Execute the entire test case: login, create space, create project, and verify RStudio IDE.
    Args:
        username: Username for login
        password: Password for login
    """
    driver = setup_driver()
    try:
        print_bold("1. LOGIN")
        login(driver, username, password)
        print_bold("2. CREATE SPACE")
        create_space(driver)
        print_bold("3. CREATE PROJECT WITHIN SPACE CREATED ABOVE")
        create_project_in_space(driver)
        print_bold("4. VERIFY RSTUDIO IDE")
        verify_rstudio_ide(driver)
    finally:
        driver.quit()  # Closing browser after the test
        print("All screenshots have been saved in the 'screenshots' folder located in the current directory.")
        print("Completed by Kanika Grover")

# Execute the test script with credentials from command-line arguments
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python automated_test_posit_cloud.py <username> <password>")
        sys.exit(1)
    else:
        run_test(sys.argv[1], sys.argv[2])
