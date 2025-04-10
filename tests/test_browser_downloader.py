import os
import platform
import shutil
import httpx
import pytest
import zipfile

from pathlib import Path
from typing import Generator, Optional
# Using pytest-mock instead of unittest.mock

from anti_judol.download import BrowserDownloader


class TestBrowserDownloader:
    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        temp_path = Path('temp/test_browser_downloader')
        temp_path.mkdir(parents=True, exist_ok=True)
        yield temp_path

        if temp_path.exists():
            shutil.rmtree(temp_path)

    @pytest.fixture
    def downloader(self, temp_dir: Path) -> BrowserDownloader:
        return BrowserDownloader(
            download_dir=temp_dir / 'bin',
            timeout=600
        )

    @pytest.fixture
    def mock_http_client(self, mocker):
        mock_client = mocker.patch('httpx.Client')
        mock_instance = mocker.MagicMock()
        mock_client.return_value = mock_instance

        mock_response = mocker.MagicMock()
        mock_response.http_version = '2'
        mock_response.headers = {'content-length': '1000000'}
        mock_response.iter_bytes.return_value = [b'mock data']

        mock_instance.stream.return_value.__enter__.return_value = mock_response

        yield mock_instance

    def find_chrome_executable(self, directory: Path) -> Optional[Path]:
        # Chrome executable names by platform
        chrome_names = {
            'windows': ['chrome.exe', 'chromium.exe'],
            'linux': ['chrome', 'chromium', 'chrome-linux', 'chromium-linux']
        }

        system = platform.system().lower()
        if system not in ['windows', 'linux']:
            pytest.skip(f'Unsupported platform for testing: {system}')

        # Get the list of possible chrome executable names for the current platform
        possible_names = chrome_names.get(system, [])

        # Search for the executable recursively
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.lower() == name.lower() for name in possible_names):
                    return Path(root) / file

        # If we couldn't find the exact executable, look for files that might contain 'chrome' or 'chromium'
        for root, _, files in os.walk(directory):
            for file in files:
                file_lower = file.lower()
                if ('chrome' in file_lower or 'chromium' in file_lower) and (
                    (system == 'windows' and file_lower.endswith('.exe')) or
                    (system == 'linux' and not file_lower.endswith('.'))
                ):
                    return Path(root) / file

        return None

    def test_platform_detection(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(platform, 'system', lambda: 'Windows')
        downloader = BrowserDownloader()
        assert downloader.platform_type == 'windows'
        assert downloader.chrome_executable == 'chrome.exe'

        monkeypatch.setattr(platform, 'system', lambda: 'Linux')
        downloader = BrowserDownloader()
        assert downloader.platform_type == 'linux'
        assert downloader.chrome_executable == 'chrome'

        monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
        with pytest.raises(ValueError, match='Unsupported platform'):
            BrowserDownloader()

    def test_download_and_extract(self, downloader: BrowserDownloader, temp_dir: Path, mock_http_client, mocker):
        mock_zip = mocker.patch('zipfile.ZipFile')
        mock_zip_instance = mocker.MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_instance

        mock_zip_instance.infolist.return_value = [mocker.MagicMock()]

        chrome_dir = downloader.download()

        assert chrome_dir.exists()
        assert chrome_dir.is_dir()
        assert (chrome_dir / downloader.chrome_executable).exists()

        mock_http_client.stream.assert_called_once()
        mock_zip.assert_called_once()

    def test_download_with_custom_filename(self, downloader: BrowserDownloader, temp_dir: Path, mock_http_client, mocker):
        mock_zip = mocker.patch('zipfile.ZipFile')
        mock_zip_instance = mocker.MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_instance

        mock_zip_instance.infolist.return_value = [mocker.MagicMock()]

        custom_filename = 'custom_chrome'
        chrome_dir = downloader.download(filename=custom_filename)

        zip_path = downloader.download_dir / f'{custom_filename}.zip'
        assert zip_path.exists()
        assert chrome_dir.exists()
        assert (chrome_dir / downloader.chrome_executable).exists()

        mock_http_client.stream.assert_called_once()
        mock_zip.assert_called_once()
