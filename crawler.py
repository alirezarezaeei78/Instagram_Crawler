import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException  # Updated import
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv
from crawler_utils import profile_username, validate_configuration

load_dotenv()


# ------------------------------------------------------------------------------
# USER CONFIGURATION
# ------------------------------------------------------------------------------
INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "")
INSTAGRAM_PASSWORD = os.getenv("INSTAGRAM_PASSWORD", "")
TARGET_USER = os.getenv("TARGET_USER", "")
OUTPUT_FILE       = "followers_of_instagram.csv"
SCROLL_LIMIT      = 10                  # <-- how many scroll attempts to load more followers
TIMEOUT           = 15                  # <-- max wait time for element loads
# ------------------------------------------------------------------------------

def init_driver(headless=False):
    """
    Initializes the Chrome WebDriver using Selenium Manager for portable driver discovery.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    # Optional: reduce log noise
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_instagram(driver, username, password, timeout=TIMEOUT):
    """
    Logs into Instagram and handles cookie banners or other pop-ups.
    Raises an Exception if login fails (e.g., incorrect credentials).
    """
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, timeout)

    # 1. Handle cookie pop-up (if it appears)
    #    The text of the cookie button can vary by region
    try:
        cookie_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Allow essential')]"))
        )
        cookie_button.click()
        print("Cookie banner dismissed.")
    except:
        print("No (or different) cookie banner found.")

    # 2. Wait for login fields to appear
    try:
        username_input = wait.until(
            EC.visibility_of_element_located((By.NAME, "username"))
        )
        password_input = wait.until(
            EC.visibility_of_element_located((By.NAME, "password"))
        )
    except:
        # Fallback if NAME='username' or NAME='password' changed
        print("Could not locate login fields by NAME. Trying alternative locators.")
        username_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        password_input = wait.until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )

    # 3. Enter credentials & submit
    username_input.clear()
    username_input.send_keys(username)
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)

    # 4. Wait a bit for the main feed or next prompt
    time.sleep(5)

    # 5. Handle "Save your login info?" or "Turn on Notifications?" if it appears
    #    This text can vary
    try:
        not_now_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
        )
        not_now_btn.click()
        print("Dismissed 'Save Info'/'Notifications' prompt.")
    except:
        pass

    # 6. Final check to ensure we are logged in
    time.sleep(3)
    if "login" in driver.current_url.lower():
        raise Exception("Login may have failed. Still on /login page. Check credentials or new login prompts.")

def scrape_followers(driver, target_user, scroll_limit=SCROLL_LIMIT, timeout=TIMEOUT):
    """
    Navigate to target user's profile, open the followers list, then scroll
    to load and collect followers. Returns a list of usernames.
    """
    wait = WebDriverWait(driver, timeout)

    # 1. Go to the target user's profile
    profile_url = f"https://www.instagram.com/{target_user}/"
    driver.get(profile_url)
    time.sleep(3)

    # 2. Click the 'followers' link
    try:
        followers_link = wait.until(
            EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "followers"))
        )
        followers_link.click()
    except:
        raise Exception(f"Could not find a followers link on profile: {profile_url}")

    # 3. Wait for the dialog containing the followers list
    time.sleep(2)
    try:
        wait.until(
            EC.visibility_of_element_located((By.XPATH, "//div[@role='dialog']"))
        )
    except:
        raise Exception("Followers dialog didn't appear. Possibly a private account or unexpected layout.")

    followers = set()
    last_height = 0

    for i in range(scroll_limit):
        # Each iteration, we re-locate the popup to avoid stale references
        try:
            popup = driver.find_element(By.XPATH, "//div[@role='dialog']")
        except:
            print("Could not re-locate the followers dialog. Possibly closed or changed.")
            break

        # Locate follower elements
        user_elems = popup.find_elements(By.XPATH, ".//a[contains(@href, '/') and not(contains(@href, '/accounts/'))]")
        for elem in user_elems:
            href = elem.get_attribute("href")
            username = profile_username(href)
            if username:
                followers.add(username)

        # Scroll
        try:
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", popup)
        except StaleElementReferenceException:
            print("Stale element while scrolling. Re-locating popup next iteration.")
            continue

        time.sleep(2)  # wait for more content to load

        # Check if new content loaded
        try:
            new_height = driver.execute_script("return arguments[0].scrollHeight", popup)
            if new_height == last_height:
                print("No more followers loaded. Stopping scroll.")
                break
            last_height = new_height
        except StaleElementReferenceException:
            print("Stale element while checking scrollHeight. Re-locating popup next iteration.")
            continue

    return sorted(followers)

def main():
    validate_configuration(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD, TARGET_USER, SCROLL_LIMIT)
    driver = init_driver(headless=False)  # If True, runs without opening a visible browser
    try:
        print("Logging in...")
        login_to_instagram(driver, INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
        print("Login successful. Now scraping followers for:", TARGET_USER)

        followers_list = scrape_followers(driver, TARGET_USER, scroll_limit=SCROLL_LIMIT)
        print(f"Found {len(followers_list)} followers for user '{TARGET_USER}'.")

        # 5. Save to CSV
        if not os.path.exists("data"):
            os.makedirs("data")
        output_path = os.path.join("data", OUTPUT_FILE)

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["follower", "followed"])
            for follower in followers_list:
                writer.writerow([follower, TARGET_USER])

        print(f"Follower data saved to: {output_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
