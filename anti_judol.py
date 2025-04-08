import argparse
import os
import sys
import logging
from pathlib import Path

from anti_judol.actions.auth import login, status
from anti_judol.actions.remover import remover

from anti_judol.download import BrowserDownloader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_browser():
    logger.info("Checking browser configuration...")
    workspace_dir = Path(os.path.abspath(os.path.dirname(__file__)))
    logger.info(f"Workspace directory: {workspace_dir}")

    bin_dir = workspace_dir / "bin"
    chrome_dir = bin_dir / "chrome"
    chrome_binary = chrome_dir / "chrome.exe"
    user_data_dir = bin_dir / "User Data"

    logger.debug(f"Chrome binary path: {chrome_binary}")
    logger.debug(f"User data directory: {user_data_dir}")

    if not chrome_binary.exists():
        logger.info("Browser not found. Downloading...")
        try:
            downloader = BrowserDownloader(download_dir=bin_dir)

            logger.info("Starting browser download...")
            chrome_dir = downloader.download()

            logger.info(f"Browser downloaded and extracted to: {chrome_dir}")

            if not chrome_binary.exists():
                error_msg = f"Chrome executable not found at expected location: {chrome_binary}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info("Browser download completed successfully")
        except Exception as e:
            logger.error(f"Error during browser download: {e}")
            sys.exit(1)
    else:
        logger.info("Browser already exists, skipping download")

    if not user_data_dir.exists():
        logger.info(f"Creating user data directory: {user_data_dir}")
        user_data_dir.mkdir(parents=True, exist_ok=True)
        logger.info("User data directory created successfully")
    else:
        logger.info("User data directory already exists")

    logger.info("Browser configuration check completed")
    return chrome_binary, user_data_dir

def flags():
    flag = argparse.ArgumentParser()

    auth = flag.add_argument_group("auth options")
    auth.add_argument("--login", action="store_true", help="log in into youtube account")
    auth.add_argument("--status", action="store_true", help="check login status")
    auth.add_argument("--logout", action="store_true", help="logout")

    action = flag.add_argument_group("action options")
    remove_group = action.add_mutually_exclusive_group()
    remove_group.add_argument('--remove_urls', type=str, nargs='+', help='remove comments from specific video URLs (cannot be used with --remove_txt)')
    remove_group.add_argument('--remove_txt', type=str, help='remove comments from video URLs listed in a text file (cannot be used with --remove_urls)')

    return flag.parse_args()


if __name__ == "__main__":
    args = flags()

    chrome_binary, user_data_dir = check_browser()
    logger.debug(f"Using chrome binary: {chrome_binary}")
    logger.debug(f"Using user data directory: {user_data_dir}")

    if args.login:
        logger.info("Starting login process...")
        login(chrome_binary, user_data_dir)

    # Handle comment removal
    if args.remove_urls or args.remove_txt:
        logger.info("Starting comment removal process...")

        urls = []

        # Get URLs from text file if specified
        if args.remove_txt:
            try:
                with open(args.remove_txt, 'r') as f:
                    urls = [line.strip() for line in f.readlines() if line.strip()]
                    if not urls:
                        logger.warning(f"No URLs found in file: {args.remove_txt}")
                        sys.exit(1)
                    logger.info(f"Loaded {len(urls)} URLs from {args.remove_txt}")
            except FileNotFoundError:
                logger.error(f"File not found: {args.remove_txt}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"Error reading file {args.remove_txt}: {e}")
                sys.exit(1)

        # Use directly provided URLs
        elif args.remove_urls:
            urls = args.remove_urls
            logger.info(f"Using {len(urls)} URLs provided via command line")

        # Process the URLs
        if not urls:
            logger.error("No URLs found for comment removal")
            sys.exit(1)

        logger.info(f"Removing comments from {len(urls)} videos")
        remover(chrome_binary, user_data_dir, urls)

    if args.status:
        logger.info("Checking login status...")
        status(chrome_binary, user_data_dir)
