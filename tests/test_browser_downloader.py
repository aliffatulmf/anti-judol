import os
import platform
import shutil

import pytest

from pathlib import Path
from typing import Generator, Optional

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
            timeout=600  # Increase timeout for slow connections
        )

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

    @pytest.fixture
    def cleanup_after_test(self, downloader: BrowserDownloader) -> Generator[None, None, None]:
        yield
        # Cleanup: remove the downloaded and extracted files
        try:
            if hasattr(downloader, 'download_dir') and downloader.download_dir.exists():
                shutil.rmtree(downloader.download_dir)
        except Exception as e:
            print(f'Warning: Failed to clean up download directory: {e}')

        # No need to clean up temp_dir as it's no longer used in BrowserDownloader

    def test_download_and_extract(self, downloader: BrowserDownloader, temp_dir: Path, cleanup_after_test):
        # temp_dir is used by downloader fixture
        # cleanup_after_test is a fixture that will run after the test to clean up
        # Skip test if running in CI environment to avoid long downloads
        if os.environ.get('CI') == 'true':
            pytest.skip('Skipping download test in CI environment')

        try:
            # Download and extract the browser
            chrome_dir = downloader.download()

            # Verify that the extracted directory exists
            assert chrome_dir.exists(), f'Chrome directory does not exist: {chrome_dir}'
            assert chrome_dir.is_dir(), f'Chrome directory is not a directory: {chrome_dir}'

            # Find the Chrome executable
            chrome_exe = self.find_chrome_executable(chrome_dir)

            # Verify that the Chrome executable exists
            assert chrome_exe is not None, f'Chrome executable not found in {chrome_dir}'
            assert chrome_exe.exists(), f'Chrome executable does not exist: {chrome_exe}'

            # Verify that the Chrome executable is executable (on Linux)
            if platform.system().lower() == 'linux':
                assert os.access(chrome_exe, os.X_OK), f'Chrome executable is not executable: {chrome_exe}'

            # Log the path to the Chrome executable
            print(f'Found Chrome executable at: {chrome_exe}')

        except Exception as e:
            pytest.fail(f'Download and extract test failed: {e}')

    def test_download_with_custom_filename(self, downloader: BrowserDownloader, temp_dir: Path, cleanup_after_test):
        # temp_dir is used by downloader fixture
        # cleanup_after_test is a fixture that will run after the test to clean up
        # Skip test if running in CI environment to avoid long downloads
        if os.environ.get('CI') == 'true':
            pytest.skip('Skipping download test in CI environment')

        try:
            # Download with a custom filename
            custom_filename = 'custom_chrome_download'
            chrome_dir = downloader.download(filename=custom_filename)

            # Verify that the zip file exists with the custom name
            zip_path = downloader.download_dir / f'{custom_filename}.zip'
            assert zip_path.exists(), f'Downloaded zip file does not exist: {zip_path}'

            # Verify that the extracted directory exists
            assert chrome_dir.exists(), f'Chrome directory does not exist: {chrome_dir}'

            # Find the Chrome executable
            chrome_exe = self.find_chrome_executable(chrome_dir)

            # Verify that the Chrome executable exists
            assert chrome_exe is not None, f'Chrome executable not found in {chrome_dir}'
            assert chrome_exe.exists(), f'Chrome executable does not exist: {chrome_exe}'

        except Exception as e:
            pytest.fail(f'Download with custom filename test failed: {e}')

    def test_platform_detection(self, monkeypatch: pytest.MonkeyPatch):
        # Test Windows detection
        monkeypatch.setattr(platform, 'system', lambda: 'Windows')
        downloader = BrowserDownloader()
        assert downloader.platform_type == 'windows'

        # Test Linux detection
        monkeypatch.setattr(platform, 'system', lambda: 'Linux')
        downloader = BrowserDownloader()
        assert downloader.platform_type == 'linux'

        # Test unsupported platform
        monkeypatch.setattr(platform, 'system', lambda: 'Darwin')
        with pytest.raises(ValueError, match='Unsupported platform'):
            BrowserDownloader()

        # We can't test platform override anymore since it's not supported in the new implementation
        # Just verify that the platform detection works correctly
