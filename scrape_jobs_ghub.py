from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import Select
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os  # For environment variables

# Load environment variables
SCRAPE_URL = os.getenv(
    "SCRAPE_URL",
    "https://harris-uchicago-csm.symplicity.com/students/app/jobs/discover",
)
LOGIN_URL = os.getenv(
    "LOGIN_URL",
    "https://harris-uchicago-csm.symplicity.com/students/index.php?signin_tab=0",
)
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


def set_up():
    # Set up Chrome options
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    # Use WebDriver Manager to automatically handle the ChromeDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )
    return driver


def execute_scraping(driver):

    driver.get(LOGIN_URL)

    # Wait for the page to load
    time.sleep(3)

    # Locate the username and password input elements using their IDs
    username_input = driver.find_element(By.ID, "username")
    password_input = driver.find_element(By.ID, "password")

    # Fill in the credentials
    username_input.send_keys(USERNAME)
    password_input.send_keys(PASSWORD)

    # Submit the form
    password_input.send_keys(Keys.RETURN)

    # Wait for login and page load
    time.sleep(5)

    driver.get(SCRAPE_URL)

    # Wait for the page to load
    time.sleep(3)

    # Locate the search input field by ID and enter the phrase "data"
    search_input = driver.find_element(By.ID, "jobs-keyword-input")
    search_input.send_keys("data")

    # Wait a second for the input to register
    time.sleep(1)

    # Locate the "Search" button by its class and click it
    search_button = driver.find_element(
        By.XPATH, "//button[contains(@class, 'btn_alt-default') and text()='Search']"
    )
    search_button.click()

    time.sleep(5)

    select_element = driver.find_element(By.XPATH, '//select[@aria-label="Sort by"]')

    # Initialize the Select object to work with the dropdown
    select = Select(select_element)

    # Select the option by value
    select.select_by_value("!postdate")
    time.sleep(5)

    wait = WebDriverWait(driver, 10)
    list_items = wait.until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "list-item"))
    )

    jobs = []
    for item in list_items:
        title = item.find_element(By.CSS_SELECTOR, ".list-item-title span").text
        subtitle = item.find_element(By.CSS_SELECTOR, ".list-item-subtitle span").text
        days = item.find_element(By.CSS_SELECTOR, ".list-secondary-action span").text

        jobs.append({"title": title, "subtitle": subtitle, "days_posted": days})

    return jobs


def send_email(jobs):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL").split(
        ","
    )  # Multiple recipients in env var, separated by commas

    # Create the email content
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(
        receiver_email
    )  # Join the list into a comma-separated string
    message["Subject"] = "Daily Job Listings Update"

    # Build the email body
    body = "Here are today's job listings:\n\n"
    for job in jobs:
        body += f"Title: {job['title']}\n"
        body += f"Subtitle: {job['subtitle']}\n"
        body += f"Days Posted: {job['days_posted']}\n"
        body += "---\n"

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the Gmail server
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    driver = set_up()
    jobs = execute_scraping(driver)
    send_email(jobs)
