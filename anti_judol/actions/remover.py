import json
import os
import logging

from pathlib import Path
from seleniumbase import SB, BaseCase
from seleniumbase.common.exceptions import NoSuchElementException
from seleniumbase.fixtures.base_case import By

from anti_judol.model import LoadModel

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

XPATH_ROOT: str = '//*[@id="contents"]'
XPATH_CHILDREN: str = f'{XPATH_ROOT}/ytd-comment-thread-renderer'


def get_comment_xpath(index: int) -> str:
    return f'{XPATH_CHILDREN}[{index}]/ytd-comment-view-model/div[3]/div[2]/ytd-expander/div/yt-attributed-string/span'

def get_author_xpath(index: int) -> str:
    return f'{XPATH_CHILDREN}[{index}]/ytd-comment-view-model/div[3]/div[2]/div/div[2]/h3/a/span'

def get_option_xpath(index: int) -> str:
    return f'{XPATH_CHILDREN}[{index}]/ytd-comment-view-model/div[3]/div[3]/ytd-menu-renderer/yt-icon-button/button'

def remove_comment(sb: BaseCase, index: int) -> bool:
    REMOVE_BUTTON_XPATH = '//*[@id="items"]/ytd-menu-navigation-item-renderer[2]'
    CONFIRM_BUTTON_XPATH = '//*[@id="confirm-button"]/yt-button-shape/button'

    logger.info('Checking option button')
    if sb.wait_for_element_clickable(get_option_xpath(index), By.XPATH, 5.0):
        logger.info('Found option button')
        sb.sleep(0.5)
        logger.info('Clicking option button')
        sb.click(get_option_xpath(index), By.XPATH, 5.0)

    logger.info('Checking remove button')
    if sb.wait_for_element_clickable(REMOVE_BUTTON_XPATH, By.XPATH, 5.0):
        logger.info('Found remove button')
        sb.sleep(0.5)
        logger.info('Clicking remove button')
        sb.click(REMOVE_BUTTON_XPATH, By.XPATH, 5.0)

    logger.info('Checking confirm button')
    if sb.wait_for_element_clickable(CONFIRM_BUTTON_XPATH, By.XPATH, 5.0):
        logger.info('Found confirm button')
        sb.sleep(0.5)
        logger.info('Clicking confirm button')
        sb.click(CONFIRM_BUTTON_XPATH, By.XPATH, 5.0)

        sb.sleep(1.5)
        return True
    return False


def _remover(model: LoadModel, chrome_binary: Path, user_data_dir: Path, url: str) -> None:
    cookie_path = os.path.join(user_data_dir, 'AntiJudol.json')
    if not os.path.exists(cookie_path):
        logger.warning('User not logged in')
        return

    with open(cookie_path) as f:
        cookies = json.load(f)

    with SB(
        uc=True,
        browser='chrome',
        user_data_dir=str(user_data_dir),
        binary_location=str(chrome_binary),
        chromium_arg='--mute-audio',
    ) as sb:
        sb: BaseCase = sb

        logger.info('Navigating to YouTube homepage')
        sb.get('https://youtube.com')
        sb.maximize_window()
        sb.wait_for_ready_state_complete(timeout=60)
        sb.sleep(1.0)

        logger.info('Adding cookies for authentication')
        for cookie in cookies:
            try:
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                if 'expiry' in cookie:
                    del cookie['expiry']
                logger.debug(f'Adding cookie: {cookie}')
                sb.add_cookie(cookie)
            except Exception as e:
                logger.error(f'Error adding cookie: {e}')

        logger.info('Navigating to YouTube Video')
        sb.get(url)
        sb.wait_for_ready_state_complete(timeout=60)
        sb.sleep(1.0)

        logger.info('Checking sort by button')
        sb.slow_scroll_to('//*[@id="comments"]', By.XPATH, 10.0)
        sb.wait_for_text_visible('Sort by', '//*[@id="sort-menu"]/yt-sort-filter-sub-menu-renderer/yt-dropdown-menu', By.XPATH, 10.0)
        sb.click('//*[@id="sort-menu"]/yt-sort-filter-sub-menu-renderer/yt-dropdown-menu', By.XPATH)

        logger.info('Selecting newest first')
        sb.wait_for_text_visible('Newest first', timeout=10.0)
        sb.click('//*[@id="menu"]/a[2]', By.XPATH)

        logger.info('Waiting for comments to load')
        sb.sleep(3.0)

        index: int = 1
        fails: int = 0
        max_fails: int = 3

        while fails < max_fails:
            try:
                logger.debug(f'Checking comment {index}')
                sb.wait_for_element_visible(get_comment_xpath(index), By.XPATH, 10.0)

                sb.scroll_to(get_comment_xpath(index), By.XPATH)

                logger.debug(f'Getting comment {index}')
                comment_text = sb.get_text_content(get_comment_xpath(index), By.XPATH, 10.0)

                logger.debug(f'Checking comment {index}')
                if model.predict_int([comment_text]) == [1]:
                    logger.debug(f'Removing comment {index}')
                    if remove_comment(sb, index):
                        fails = 0
                        continue
                    else:
                        logger.warning(f'Failed to remove comment {index}')
                        index += 1
                        continue
                else:
                    logger.debug(f'Skipping comment {index}')

                fails = 0
                index += 1

                logger.debug(f'Comment {index}: {comment_text}')
            except NoSuchElementException:
                fails += 1
                logger.warning(f'Failed to find comment {index} ({fails}/{max_fails})')

                sb.execute_script('window.scrollBy(0, 500);')
                sb.sleep(1)
            except Exception as e:
                logger.error(f'Unexpected Error: {e}')
                break

        logger.info('Assumptively finished')

def remover(chrome_binary: Path, user_data_dir: Path, urls: list[str]):
    model = LoadModel('data/models/model.pkl')
    for url in urls:
        _remover(model, chrome_binary, user_data_dir, url)
