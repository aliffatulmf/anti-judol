import logging
import subprocess
import platform
from typing import List, Optional


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_windows_pids(name: str, location: str) -> List[str]:
    pids = []
    wmic_cmd = ['wmic', 'process', 'where', f'name=\'{name}\' and executablepath like \'%{location}%\'', 'get', 'processid', '/format:list']
    logger.info(f'Finding processes: {" ".join(wmic_cmd)}')
    wmic_result = subprocess.run(wmic_cmd, capture_output=True, text=True)

    if wmic_result.returncode == 0:
        for line in wmic_result.stdout.splitlines():
            if line.strip().startswith('ProcessId='):
                pid = line.strip().split('=')[1].strip()
                if pid:
                    pids.append(pid)
    else:
        logger.error(f'Failed to find process: {wmic_result.stderr}')

    return pids


def terminate_windows_pid(pid: str, force_kill: bool) -> bool:
    cmd = ['taskkill']
    if force_kill:
        cmd.append('/F')
    cmd.extend(['/PID', pid])

    logger.info(f'Executing command: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        return True
    else:
        logger.error(f'Failed to terminate process with PID {pid}: {result.stderr}')
        return False


def terminate_windows_proc(name: str, location: Optional[str], force_kill: bool) -> bool:
    found = False

    try:
        if location:
            pids = find_windows_pids(name, location)

            if pids:
                found = True
                for pid in pids:
                    if not terminate_windows_pid(pid, force_kill):
                        found = False

                if found:
                    logger.info(f'Process \'{name}\' from location \'{location}\' successfully terminated.')
            else:
                logger.warning(f'Process \'{name}\' from location \'{location}\' not found.')
        else:
            cmd = ['taskkill']
            if force_kill:
                cmd.append('/F')
            cmd.extend(['/IM', name])

            logger.info(f'Executing command: {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f'Process \'{name}\' successfully terminated.')
                found = True
            elif 'not found' in result.stderr.lower():
                logger.warning(f'Process \'{name}\' not found.')
            else:
                logger.error(f'Failed to terminate process: {result.stderr}')
    except Exception as e:
        logger.error(f'Error terminating Windows process: {str(e)}')

    return found


def terminate_linux_proc(name: str, location: Optional[str], force_kill: bool) -> bool:
    found = False

    try:
        if location:
            pattern = f'{location}.*{name}'
            if force_kill:
                cmd = ['pkill', '-9', '-f', pattern]
            else:
                cmd = ['pkill', '-f', pattern]

            logger.info(f'Executing command: {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f'Process \'{name}\' from location \'{location}\' successfully terminated.')
                found = True
            elif result.returncode == 1:
                logger.warning(f'Process \'{name}\' from location \'{location}\' not found.')
            else:
                logger.error(f'Failed to terminate process: {result.stderr}')
        else:
            if force_kill:
                cmd = ['pkill', '-9', '-f', name]
            else:
                cmd = ['pkill', '-f', name]

            logger.info(f'Executing command: {" ".join(cmd)}')
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f'Process \'{name}\' successfully terminated.')
                found = True
            elif result.returncode == 1:
                logger.warning(f'Process \'{name}\' not found.')
            else:
                logger.error(f'Failed to terminate process: {result.stderr}')
    except Exception as e:
        logger.error(f'Error terminating Linux process: {str(e)}')

    return found


def find_and_terminate(name: str, location: Optional[str] = None, force_kill: bool = False) -> bool:
    os_type = platform.system().lower()
    found = False

    try:
        if os_type == 'windows':
            found = terminate_windows_proc(name, location, force_kill)
        elif os_type == 'linux' or os_type == 'darwin':
            found = terminate_linux_proc(name, location, force_kill)
        else:
            logger.error(f'Unsupported operating system: {os_type}')
    except Exception as e:
        logger.error(f'Error terminating process: {str(e)}')

    return found
