#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test script for BrowserDownloader class.
This script tests if the browser download functionality works correctly.
"""

import sys
import zipfile
from pathlib import Path
import tempfile
import shutil

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anti_judol.download import BrowserDownloader


def verify_zip_file(file_path: Path) -> bool:
    """
    Verify if the downloaded file is a valid zip file.

    Args:
        file_path: Path to the zip file

    Returns:
        True if the file is a valid zip file, False otherwise
    """
    if not file_path.exists():
        print(f"Error: File does not exist: {file_path}")
        return False

    # Check file size
    file_size = file_path.stat().st_size
    if file_size == 0:
        print(f"Error: File is empty: {file_path}")
        return False

    print(f"File size: {file_size / (1024 * 1024):.2f} MB")

    # Try to open the zip file
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # List the first 5 files in the zip
            file_list = zip_ref.namelist()
            print(f"Zip file contains {len(file_list)} files/directories")
            print("First 5 entries in the zip file:")
            for i, name in enumerate(file_list[:5]):
                print(f"  {i+1}. {name}")

            # Test the integrity of the zip file
            result = zip_ref.testzip()
            if result is not None:
                print(f"Error: Bad file in zip: {result}")
                return False

            return True
    except zipfile.BadZipFile:
        print(f"Error: Not a valid zip file: {file_path}")
        return False
    except Exception as e:
        print(f"Error verifying zip file: {e}")
        return False


def test_download_browser():
    """Test downloading the browser and verify the downloaded file."""
    print("Testing browser download functionality...")

    # Create a temporary directory for the download
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        # Create a downloader with a small timeout for testing
        downloader = BrowserDownloader(download_dir=temp_dir, timeout=60)

        print(f"Detected platform: {downloader.platform_type}")
        print(f"Detected architecture: {downloader.architecture}")

        # Download the browser
        print("Starting download...")
        downloaded_file = downloader.download()
        print(f"Download completed: {downloaded_file}")

        # Verify the downloaded file
        print("\nVerifying downloaded file...")
        is_valid_zip = verify_zip_file(downloaded_file)
        if is_valid_zip:
            print("\n✅ TEST PASSED: Successfully downloaded and verified the browser zip file.")
        else:
            print("\n❌ TEST FAILED: The downloaded file is not a valid zip file.")
        assert is_valid_zip, "The downloaded file is not a valid zip file."

    except Exception as e:
        print(f"\n❌ TEST FAILED: Error during download: {e}")
        assert False, f"Error during download: {e}"
    finally:
        # Clean up the temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to clean up temporary directory: {e}")


def test_download_with_custom_parameters():
    """Test downloading the browser with custom parameters."""
    print("\nTesting browser download with custom parameters...")

    # Create a temporary directory for the download
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        # Create a downloader with custom parameters
        downloader = BrowserDownloader(
            download_dir=temp_dir,
            timeout=60                # Short timeout for testing
        )

        # Note: platform_type and architecture are set automatically based on the system
        # We can't override them through parameters

        print(f"Custom platform: {downloader.platform_type}")
        print(f"Custom architecture: {downloader.architecture}")

        # Download with custom filename
        custom_filename = "chromium_test.zip"
        print(f"Starting download with custom filename: {custom_filename}")
        downloaded_file = downloader.download(filename=custom_filename)
        print(f"Download completed: {downloaded_file}")

        # Verify the downloaded file
        print("\nVerifying downloaded file...")
        is_valid_zip = verify_zip_file(downloaded_file)
        if is_valid_zip:
            print("\n✅ TEST PASSED: Successfully downloaded and verified the browser zip file with custom parameters.")
        else:
            print("\n❌ TEST FAILED: The downloaded file is not a valid zip file.")
        assert is_valid_zip, "The downloaded file is not a valid zip file."

    except Exception as e:
        print(f"\n❌ TEST FAILED: Error during download with custom parameters: {e}")
        assert False, f"Error during download with custom parameters: {e}"
    finally:
        # Clean up the temporary directory
        try:
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
        except Exception as e:
            print(f"Warning: Failed to clean up temporary directory: {e}")


if __name__ == "__main__":
    # Run the tests
    print("=== BROWSER DOWNLOADER TESTS ===\n")

    # Test with auto-detected parameters
    auto_test_result = test_download_browser()

    # Test with custom parameters
    custom_test_result = test_download_with_custom_parameters()

    # Print overall result
    print("\n=== TEST SUMMARY ===")
    print(f"Auto-detection test: {'PASSED' if auto_test_result else 'FAILED'}")
    print(f"Custom parameters test: {'PASSED' if custom_test_result else 'FAILED'}")

    if auto_test_result and custom_test_result:
        print("\n✅ ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ SOME TESTS FAILED")
        sys.exit(1)
