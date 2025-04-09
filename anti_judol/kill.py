import logging
import subprocess
import platform


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_and_terminate(process_name, force_kill=False):
    os_type = platform.system().lower()
    found = False

    try:
        if os_type == 'windows':
            cmd = ['taskkill']
            if force_kill:
                cmd.append('/F')
            cmd.extend(['/IM', process_name])

            logger.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Process '{process_name}' successfully terminated.")
                found = True
            elif "not found" in result.stderr.lower():
                logger.warning(f"Process '{process_name}' not found.")
            else:
                logger.error(f"Failed to terminate process: {result.stderr}")

        elif os_type == 'linux' or os_type == 'darwin':
            if force_kill:
                cmd = ['pkill', '-9', '-f', process_name]
            else:
                cmd = ['pkill', '-f', process_name]

            logger.info(f"Executing command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                logger.info(f"Process '{process_name}' successfully terminated.")
                found = True
            elif result.returncode == 1:
                logger.warning(f"Process '{process_name}' not found.")
            else:
                logger.error(f"Failed to terminate process: {result.stderr}")
        else:
            logger.error(f"Unsupported operating system: {os_type}")
    except Exception as e:
        logger.error(f"Error terminating process: {str(e)}")

    return found
