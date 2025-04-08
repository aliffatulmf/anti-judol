import time
import json
import logging

from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from seleniumbase import Driver
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from seleniumbase import SB
from seleniumbase import BaseCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def login(chrome_binary: Path, user_data_dir: Path):
    driver: ChromiumDriver = Driver(uc=True, browser="chrome", user_data_dir=str(user_data_dir), binary_location=str(chrome_binary))
    try:
        driver.get("https://studio.youtube.com/")
        driver.maximize_window()

        try:
            dashboard = WebDriverWait(driver, 3600).until(
                EC.text_to_be_present_in_element((By.XPATH, "//h1[@theme='DASHBOARD']"), "Channel dashboard")
            )
            if dashboard:
                time.sleep(0.5)  # Add a small delay
                print("Already logged in")

                with open(user_data_dir / "AntiJudol.json", "w") as f:
                    json.dump(driver.get_cookies(), f, indent=2)

                return
        except TimeoutException:
            print("User not logged in")
    except NoSuchElementException as e:
        print(f"User not logged in: {e}")
    finally:
        driver.close()
        driver.quit()

def status(chrome_binary: Path, user_data_dir: Path):
    with SB(
        uc=True,
        browser="chrome",
        user_data_dir=str(user_data_dir),
        binary_location=str(chrome_binary),
        headless=True,
    ) as sb:
        sb: BaseCase = sb
        sb.get('https://www.youtube.com/')
        sb.wait_for_ready_state_complete(timeout=60)

        cookie_path = user_data_dir / "AntiJudol.json"
        if not cookie_path.exists():
            logger.warning('Authentication cookie not found')
            return False

        with open(cookie_path) as f:
            cookies = json.load(f)
            for cookie in cookies:
                if 'sameSite' in cookie:
                    logger.debug(f'Removing sameSite from cookie: {cookie["sameSite"]}')
                    del cookie['sameSite']
                if 'expiry' in cookie:
                    logger.debug(f'Removing expiry from cookie: {cookie["expiry"]}')
                    del cookie['expiry']
                logger.debug(f'Adding cookie to browser: {cookie}')
                sb.add_cookie(cookie)

            logger.info('Cookies added to browser')

        sb.sleep(1.0)
        sb.get('https://studio.youtube.com/')
        sb.wait_for_ready_state_complete(timeout=60)

        logger.info('Checking login status')
        if not sb.wait_for_text_visible('Channel dashboard', '//*[@id="page-title-container"]/h1', By.XPATH, 10):
            logger.warning("User not logged in")
            return False
        else:
            logger.info("User logged in")
            return True
