
import platform
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from anti_judol.kill import find_and_terminate

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestFindAndTerminate:

    @pytest.fixture
    def mock_subprocess_run(self):
        with patch('subprocess.run') as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stderr = ""
            mock_run.return_value = mock_result
            yield mock_run

    def test_find_and_terminate_windows(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            result = find_and_terminate('test.exe')
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['taskkill', '/IM', 'test.exe'],
                capture_output=True,
                text=True
            )

            mock_subprocess_run.reset_mock()

            result = find_and_terminate('test.exe', force_kill=True)
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['taskkill', '/F', '/IM', 'test.exe'],
                capture_output=True,
                text=True
            )

    def test_find_and_terminate_linux(self, mock_subprocess_run):
        with patch('platform.system', return_value='Linux'):
            result = find_and_terminate('test')
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['pkill', '-f', 'test'],
                capture_output=True,
                text=True
            )

            mock_subprocess_run.reset_mock()

            result = find_and_terminate('test', force_kill=True)
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['pkill', '-9', '-f', 'test'],
                capture_output=True,
                text=True
            )

    def test_process_not_found(self, mock_subprocess_run):
        mock_result = MagicMock()
        mock_result.returncode = 1

        if platform.system().lower() == 'windows':
            mock_result.stderr = 'ERROR: The process \'test.exe\' not found.'
        else:
            mock_result.stderr = ""

        mock_subprocess_run.return_value = mock_result
        result = find_and_terminate('test.exe')
        assert result is False

    def test_error_handling(self, mock_subprocess_run):
        mock_subprocess_run.side_effect = Exception('Test error')
        result = find_and_terminate('test.exe')
        assert result is False

    def test_unsupported_os(self):
        with patch('platform.system', return_value='Unknown'):
            result = find_and_terminate('test.exe')
            assert result is False

    def test_find_and_terminate_windows_with_location(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            mock_wmic_result = MagicMock()
            mock_wmic_result.returncode = 0
            mock_wmic_result.stdout = "ProcessId=1234\n"
            mock_wmic_result.stderr = ""

            mock_taskkill_result = MagicMock()
            mock_taskkill_result.returncode = 0
            mock_taskkill_result.stderr = ""

            mock_subprocess_run.side_effect = [mock_wmic_result, mock_taskkill_result]

            result = find_and_terminate('test.exe', location='C:\\Program Files')
            assert result is True

            assert mock_subprocess_run.call_args_list[0][0][0][0] == 'wmic'
            assert "name='test.exe'" in mock_subprocess_run.call_args_list[0][0][0][3]
            assert "executablepath like '%C:\\Program Files%'" in mock_subprocess_run.call_args_list[0][0][0][3]

            assert mock_subprocess_run.call_args_list[1][0][0][0] == 'taskkill'
            assert mock_subprocess_run.call_args_list[1][0][0][1] == '/PID'
            assert mock_subprocess_run.call_args_list[1][0][0][2] == '1234'

    def test_find_and_terminate_linux_with_location(self, mock_subprocess_run):
        with patch('platform.system', return_value='Linux'):
            result = find_and_terminate('test', location='/usr/bin')
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['pkill', '-f', '/usr/bin.*test'],
                capture_output=True,
                text=True
            )

            mock_subprocess_run.reset_mock()

            result = find_and_terminate('test', force_kill=True, location='/usr/bin')
            assert result is True
            mock_subprocess_run.assert_called_once_with(
                ['pkill', '-9', '-f', '/usr/bin.*test'],
                capture_output=True,
                text=True
            )


if __name__ == "__main__":
    pytest.main(['-v', __file__])
