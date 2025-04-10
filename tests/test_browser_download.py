#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for BrowserDownloader class.
This script tests if the browser download functionality works correctly.
"""

import sys
from pathlib import Path
import tempfile
import shutil
import pytest
# Using pytest-mock instead of unittest.mock

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anti_judol.download import BrowserDownloader


@pytest.fixture
def mock_http_client(mocker):
    mock_client = mocker.patch('httpx.Client')
    mock_instance = mocker.MagicMock()
    mock_client.return_value = mock_instance

    mock_response = mocker.MagicMock()
    mock_response.http_version = '2'
    mock_response.headers = {'content-length': '1000000'}
    mock_response.iter_bytes.return_value = [b'mock data']

    mock_instance.stream.return_value.__enter__.return_value = mock_response

    yield mock_instance


def test_download_browser(mock_http_client, mocker):
    """Test downloading the browser and verify the downloaded file."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        mock_zip = mocker.patch('zipfile.ZipFile')
        mock_zip_instance = mocker.MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [mocker.MagicMock()]

        downloader = BrowserDownloader(download_dir=temp_dir, timeout=60)
        chrome_dir = downloader.download()

        assert chrome_dir.exists()
        assert chrome_dir.is_dir()
        assert (chrome_dir / downloader.chrome_executable).exists()

        mock_http_client.stream.assert_called_once()
        mock_zip.assert_called_once()

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


def test_download_with_custom_parameters(mock_http_client, mocker):
    """Test downloading the browser with custom parameters."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        mock_zip = mocker.patch('zipfile.ZipFile')
        mock_zip_instance = mocker.MagicMock()
        mock_zip.return_value.__enter__.return_value = mock_zip_instance
        mock_zip_instance.infolist.return_value = [mocker.MagicMock()]

        downloader = BrowserDownloader(
            download_dir=temp_dir,
            timeout=60
        )

        custom_filename = 'custom_chrome'
        chrome_dir = downloader.download(filename=custom_filename)

        zip_path = temp_dir / f'{custom_filename}.zip'
        assert zip_path.exists()
        assert chrome_dir.exists()
        assert (chrome_dir / downloader.chrome_executable).exists()

        mock_http_client.stream.assert_called_once()
        mock_zip.assert_called_once()

    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main(['-v', __file__])
