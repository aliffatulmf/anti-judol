import logging
import os
import platform
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Dict, Optional, Union

import httpx
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BrowserDownloader:
    DOWNLOAD_URLS: Dict[str, str] = {
        'windows_x64': 'https://download-chromium.appspot.com/dl/Win_x64?type=snapshots',
        'linux_x64': 'https://download-chromium.appspot.com/dl/Linux_x64?type=snapshots'
    }

    def __init__(
        self,
        download_dir: Union[str, Path] = 'bin',
        timeout: int = 300,
    ):
        self.download_dir = Path(download_dir)
        self.timeout = timeout

        system = platform.system().lower()
        if system == 'windows':
            self.platform_type = 'windows'
            self.chrome_executable = 'chrome.exe'
        elif system == 'linux':
            self.platform_type = 'linux'
            self.chrome_executable = 'chrome'
        else:
            raise ValueError(f'Unsupported platform: {system}')

        self.architecture = 'x64'

        key = f'{self.platform_type}_{self.architecture}'
        if key not in self.DOWNLOAD_URLS:
            raise ValueError(f'Unsupported platform and architecture combination: {key}')

    def download(self, filename: Optional[str] = None) -> Path:

        if not self.download_dir.exists():
            logger.info(f'Creating directory: {self.download_dir}')
            self.download_dir.mkdir(parents=True, exist_ok=True)


        key = f'{self.platform_type}_{self.architecture}'
        url = self.DOWNLOAD_URLS.get(key, '')
        if not url:
            raise ValueError(f'No download URL for {key}')

        if filename is None:
            filename = f'chrome_{self.platform_type}_{self.architecture}.zip'
        elif not filename.endswith('.zip'):
            filename += '.zip'

        chrome_dir = self.download_dir / 'chrome'
        chrome_exe = chrome_dir / self.chrome_executable

        if chrome_exe.exists():
            logger.info(f'Chrome executable already exists: {chrome_exe}')
            return chrome_dir

        zip_path = self.download_dir / filename

        if zip_path.exists():
            logger.info(f'Zip file already exists: {zip_path}')
        else:
            logger.info(f'Downloading browser from {url} to {zip_path}')

            try:
                try:
                    client = httpx.Client(follow_redirects=True, http2=True)
                    logger.info('Using HTTP/2 for download')
                except ImportError:
                    client = httpx.Client(follow_redirects=True)
                    logger.info('HTTP/2 not available, using HTTP/1.1')

                with client:
                    with client.stream('GET', url, timeout=self.timeout) as response:
                        response.raise_for_status()
                        logger.info(f'Using HTTP/{response.http_version}')
                        total_size = int(response.headers.get('content-length', 0))

                        with open(zip_path, 'wb') as f:
                            if total_size == 0:
                                logger.warning('Content length header not found, download progress cannot be tracked')
                                for chunk in response.iter_bytes():
                                    f.write(chunk)
                            else:
                                with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024,
                                          desc=f'Downloading {filename}', leave=True, ncols=100, ascii=True) as progress_bar:
                                    for chunk in response.iter_bytes(chunk_size=8192):
                                        f.write(chunk)
                                        progress_bar.update(len(chunk))

                logger.info(f'Download completed: {zip_path}')
            except Exception as e:
                logger.error(f'Error downloading file: {e}')
                if zip_path.exists() and zip_path.stat().st_size == 0:

                    zip_path.unlink()
                raise

        if chrome_dir.exists():
            logger.info(f'Removing existing directory: {chrome_dir}')
            shutil.rmtree(chrome_dir)

        logger.info(f'Extracting {zip_path} to {chrome_dir}')
        chrome_dir.mkdir(parents=True, exist_ok=True)

        try:
            temp_extract_dir = self.download_dir / 'temp_extract'
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            temp_extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                total_files = len(zip_ref.infolist())
                with tqdm(total=total_files, desc='Extracting files', unit='files', ascii=True, ncols=100) as pbar:
                    for file in zip_ref.infolist():
                        zip_ref.extract(file, temp_extract_dir)
                        pbar.update(1)

            chrome_exe_path = self.find_chrome_executable(temp_extract_dir)
            if not chrome_exe_path:
                error_msg = f'Chrome executable not found in extracted files'
                logger.error(error_msg)
                shutil.rmtree(temp_extract_dir)
                raise ValueError(error_msg)

            logger.info(f'Moving Chrome executable to {chrome_dir}')

            chrome_parent_dir = chrome_exe_path.parent
            for item in chrome_parent_dir.iterdir():
                target_path = chrome_dir / item.name
                if target_path.exists():
                    if target_path.is_dir():
                        shutil.rmtree(target_path)
                    else:
                        target_path.unlink()
                if item.is_dir():
                    shutil.copytree(item, target_path)
                else:
                    shutil.copy2(item, target_path)

            shutil.rmtree(temp_extract_dir)

            logger.info(f'Extraction completed to: {chrome_dir}')

            chrome_exe = chrome_dir / self.chrome_executable
            if not chrome_exe.exists():
                error_msg = f'Chrome executable not found at expected location: {chrome_exe}'
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f'Chrome executable found at: {chrome_exe}')
            return chrome_dir

        except httpx.HTTPError as e:
            logger.error(f'Download failed: {e}')
            if zip_path.exists():
                zip_path.unlink()
            raise
        except Exception as e:
            logger.error(f'Error during download or extraction: {e}')

            chrome_dir = self.download_dir / 'chrome'
            if chrome_dir.exists():
                shutil.rmtree(chrome_dir)
            temp_extract_dir = self.download_dir / 'temp_extract'
            if temp_extract_dir.exists():
                shutil.rmtree(temp_extract_dir)
            if zip_path.exists():
                zip_path.unlink()
            raise

    def find_chrome_executable(self, directory: Path) -> Optional[Path]:
        executable_name = self.chrome_executable

        for root, _, files in os.walk(directory):
            for file in files:
                if file.lower() == executable_name.lower():
                    return Path(root) / file

        for root, _, files in os.walk(directory):
            for file in files:
                file_lower = file.lower()
                if 'chrome' in file_lower and (
                    (self.platform_type == 'windows' and file_lower.endswith('.exe')) or
                    (self.platform_type == 'linux' and os.access(os.path.join(root, file), os.X_OK))
                ):
                    return Path(root) / file

        return None


def main():
    try:
        downloader = BrowserDownloader()
        chrome_dir = downloader.download()
        logger.info(f'Chrome browser downloaded and extracted to: {chrome_dir}')
        return 0
    except Exception as e:
        logger.error(f'Error: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
