import csv
import logging
import os
import signal
import sys
from dataclasses import dataclass
from typing import Any, List, Optional

import pandas as pd
from selenium.webdriver.common.by import By
from seleniumbase import SB
from seleniumbase.common.exceptions import NoSuchElementException
from seleniumbase.fixtures.base_case import BaseCase


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TIMEOUT = 10
SCROLL_TIMEOUT = 2

@dataclass
class Comment:
    author: str
    text: str

@dataclass
class XPath:
    ROOT: str = '//*[@id="contents"]'
    CHILDREN: str = f'{ROOT}/ytd-comment-thread-renderer'

    @classmethod
    def comment(cls, index: int) -> str:
        return f'{cls.CHILDREN}[{index}]/ytd-comment-view-model/div[3]/div[2]/ytd-expander/div/yt-attributed-string/span'

    @classmethod
    def author(cls, index: int) -> str:
        return f'{cls.CHILDREN}[{index}]/ytd-comment-view-model/div[3]/div[2]/div/div[2]/h3/a/span'


class Scraper:
    def __init__(self, url: str, output: str, sort_by: str, max_comments: Optional[int] = None, model_path: Optional[str] = None, **kwargs):
        from anti_judol.normalizer import TextNormalizer
        from anti_judol.model import LoadModel

        self.url: str = url
        self.output: str = output
        self.sort_by: str = sort_by
        self.max_comments: Optional[int] = max_comments
        self.model_path: Optional[str] = model_path
        self.model = None

        self.chrome_headless: bool = kwargs.get('headless', False)

        if model_path and os.path.exists(model_path):
            try:
                self.model = LoadModel(model_path)
                logger.info(f'Model loaded from {model_path} with version {self.model.version}')
            except Exception as e:
                logger.error(f'Error loading model: {e}')

        self.comments: List[Comment] = []
        self.xpath: XPath = XPath()
        self.normalizer: TextNormalizer = TextNormalizer()

    def _get_output_path(self) -> str:
        return self.output

    def _ensure_output_dir(self) -> None:
        output_path = self._get_output_path()
        output_dir = os.path.dirname(os.path.abspath(output_path))
        os.makedirs(output_dir, exist_ok=True)

    def save(self) -> None:
        try:
            self._ensure_output_dir()
            output_path = self._get_output_path()

            raw_data = {
                'author': [],
                'text': []
            }

            for comment in self.comments:
                raw_data['author'].append(comment.author)
                raw_data['text'].append(comment.text)

            df = pd.DataFrame(raw_data)

            logger.info('Normalizing comments...')
            df['text'] = df['text'].apply(self.normalizer.normalize)

            logger.info('Filtering empty texts...')
            total_before = len(df)
            df = df.dropna(subset=['text'])
            df = df[df['text'].str.strip() != '']
            total_after = len(df)
            filtered_count = total_before - total_after

            if filtered_count > 0:
                logger.info(f'Filtered out {filtered_count} empty texts')

            # Add label column if model is available
            if self.model is not None:
                logger.info('Predicting labels...')
                try:
                    labels = self.model.predict_int(df['text'].tolist())
                    df['label'] = labels
                    logger.info(f'Added {len(labels)} labels')
                except Exception as e:
                    logger.error(f'Error predicting labels: {e}')
                    # Add default label 0 if prediction fails
                    df['label'] = 0
            else:
                # Add default label 0 if no model is provided
                df['label'] = 0

            logger.info('Saving to CSV...')
            df.to_csv(output_path, index=False, encoding='utf-8', escapechar='\\', quoting=csv.QUOTE_ALL)

            logger.info(f'Data saved to {output_path} with normalized text and labels')
        except Exception as e:
            logger.error(f'Error saving data to CSV: {e}')
            raise

    def _scroll_to_comment(self, sb: BaseCase, index: int) -> None:
        sb.scroll_to(self.xpath.comment(index), by=By.XPATH, timeout=SCROLL_TIMEOUT)

    def _extract_comment_data(self, sb: BaseCase, index: int) -> tuple[str, str]:
        author_path = self.xpath.author(index)
        comment_path = self.xpath.comment(index)

        author = sb.get_text_content(author_path, by=By.XPATH, timeout=SCROLL_TIMEOUT).strip()
        text = sb.get_text_content(comment_path, by=By.XPATH, timeout=SCROLL_TIMEOUT).strip()

        return author, text

    def _add_comment(self, author: str, text: str, index: int) -> bool:
        comment = Comment(author=author, text=text)
        self.comments.append(comment)
        logger.info(f'{index}. Extracted comment from {comment.author}')
        if self.max_comments is not None and len(self.comments) >= self.max_comments:
            logger.info(f'Reached maximum number of comments ({self.max_comments})')
            return True
        return False

    def _setup_sort_order(self, sb: BaseCase) -> None:
        if self.sort_by == 'newest':
            try:
                additional_section = '//*[@id="additional-section"]'
                newest_option = '//*[@id="menu"]/a[2]'

                if sb.is_element_visible(additional_section, by=By.XPATH):
                    sb.click(additional_section, by=By.XPATH)
                    if sb.wait_for_text_visible('Newest first', timeout=TIMEOUT):
                        sb.click(newest_option, by=By.XPATH, timeout=TIMEOUT)
                        logger.info('Set comment sort order to \'Newest first\'')
            except Exception as e:
                logger.warning(f'Failed to set sort order to \'newest\': {e}')

    def scrape(self) -> None:
        self.comments = []

        logger.info('Setting up signal handler for Ctrl+C...')
        def signal_handler(_sig: int, _frame: Any) -> None:
            logger.info('Ctrl+C detected. Saving comments and exiting...')
            self.save()
            sys.exit(0)

        logger.info('Installing signal handler for Ctrl+C...')
        signal.signal(signal.SIGINT, signal_handler)

        with SB(uc=True,
                browser='chrome',
                user_data_dir=os.path.join(BASE_DIR, 'bin', 'User Data'),
                binary_location=os.path.join(BASE_DIR, 'bin', 'chrome', 'chrome.exe'),
                ad_block=True,
                headless=self.chrome_headless,
                chromium_arg='--mute-audio',
                ) as sb:
            sb: BaseCase

            logger.info(f'Starting scrape for video: {self.url}')
            sb.open(self.url)
            sb.slow_scroll_to(self.xpath.ROOT, by=By.XPATH, timeout=TIMEOUT)

            self._setup_sort_order(sb)

            index = 1
            fails = 0
            max_fails = 3

            while fails < max_fails:
                try:
                    self._scroll_to_comment(sb, index)
                    author, text = self._extract_comment_data(sb, index)
                    if self._add_comment(author, text, index):
                        break

                    fails = 0
                    index += 1
                except NoSuchElementException:
                    fails += 1
                    logger.warning(f'Failed to find comment {index} ({fails}/{max_fails})')
                    sb.execute_script('window.scrollBy(0, 500);')
                    sb.sleep(1)
                except Exception as e:
                    logger.error(f'Unexpected Error: {e}')
                    break

        self.save()

if __name__ == '__main__':
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description='YouTube Comment Scraper')
    parser.add_argument('--url', required=True, help='URL of the YouTube video to scrape')
    parser.add_argument('--output', default='temp/comments.csv', help='Filename to save the comments')
    parser.add_argument('--sort_by', type=str, choices=['newest', 'top'], default='newest', help='Scrape comments sorted by newest first or top')
    parser.add_argument('--max_comments', type=int, help='Maximum number of comments to scrape')
    parser.add_argument('--model', type=str, help='Path to the model file for text classification')
    parser.add_argument('--headless', action='store_true', help='Run the scraper in headless mode')

    args = parser.parse_args()

    scraper: Scraper = Scraper(
        url=args.url,
        output=args.output,
        sort_by=args.sort_by,
        max_comments=args.max_comments,
        model_path=args.model,
        headless=args.headless,
    )

    try:
        scraper.scrape()
    except KeyboardInterrupt:
        logger.info('Scraping interrupted by user')
        scraper.save()
    except Exception as e:
        logger.error(f'Error during scraping: {e}')
        sys.exit(1)
