import psutil
import os
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_and_terminate_process(process_name, target_path, force_kill=False):
    target_path = os.path.normcase(os.path.abspath(target_path))
    found = False

    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            pinfo = proc.info
            if pinfo['name'].lower() != process_name.lower():
                continue

            exe_path = pinfo.get('exe', '')
            if not exe_path:
                continue

            if os.path.normcase(exe_path) == target_path:
                pid = pinfo['pid']
                logger.info(f"Found process {pinfo['name']} (PID: {pid})")

                try:
                    if force_kill:
                        logger.info("Force killing process...")
                        proc.kill()
                    else:
                        logger.info("Terminating process safely...")
                        proc.terminate()
                        # Wait 5 seconds for the process to terminate gracefully
                        proc.wait(timeout=5)

                    logger.info(f"Process {pid} successfully terminated.")
                    found = True
                except psutil.TimeoutExpired:
                    if not force_kill:
                        logger.warning("Process not responding, force killing...")
                        proc.kill()
                        logger.info(f"Process {pid} forcefully terminated.")
                        found = True
                except psutil.NoSuchProcess:
                    logger.info(f"Process {pid} is no longer running.")
                except psutil.AccessDenied:
                    logger.error("Permission denied to terminate this process.")
                except Exception as e:
                    logger.error(f"Failed to terminate process: {str(e)}")
                finally:
                    break  # Stop searching after process is terminated
        except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
            continue

    if not found:
        logger.warning(f"Process '{process_name}' with path {target_path} not found.")

# if __name__ == "__main__":
#     target_process = "chrome.exe"
#     target_path = r"D:\chrome\chrome.exe"

#     # Usage examples:
#     # 1. Terminate process normally (default)
#     #find_and_terminate_process(target_process, target_path)

#     # 2. Force kill process
#     #find_and_terminate_process(target_process, target_path, force_kill=True)
