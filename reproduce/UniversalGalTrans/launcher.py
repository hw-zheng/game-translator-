import sys
import os
import subprocess
import time
import signal
import threading

# Add root to path (parent of this script)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from UniversalGalTrans.core.logger import setup_logger
from UniversalGalTrans.core.config import get_config

logger = setup_logger("UGT_Launcher")

def main():
    logger.info("=== Universal Galgame Translator Launcher ===")

    # 1. Start Bridge Server
    logger.info("Starting Bridge Server...")

    # Use sys.executable to ensure we use the same python interpreter
    server_script = os.path.join("UniversalGalTrans", "core", "bridge_server.py")

    if not os.path.exists(server_script):
        logger.error(f"Could not find server script at: {server_script}")
        return

    server_process = subprocess.Popen(
        [sys.executable, server_script],
        cwd=os.getcwd()
    )
    logger.info(f"Bridge Server started (PID: {server_process.pid})")

    # Wait for server to initialize
    time.sleep(2)

    # 2. Start Overlay UI
    logger.info("Starting Overlay UI...")
    ui_script = os.path.join("UniversalGalTrans", "core", "overlay_ui.py")

    ui_process = subprocess.Popen(
        [sys.executable, ui_script],
        cwd=os.getcwd()
    )
    logger.info(f"Overlay UI started (PID: {ui_process.pid})")

    # 3. Monitor Loop
    logger.info("System is running. Close the Overlay window to exit.")

    try:
        while True:
            # Check if UI is still running
            if ui_process.poll() is not None:
                logger.info("Overlay UI closed by user. Shutting down...")
                break

            # Check if Server crashed
            if server_process.poll() is not None:
                logger.error("Bridge Server crashed unexpectedly! Shutting down...")
                break

            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt.")
    finally:
        # Cleanup
        if ui_process.poll() is None:
            logger.info("Terminating UI...")
            ui_process.terminate()

        if server_process.poll() is None:
            logger.info("Terminating Server...")
            server_process.terminate()

        logger.info("Goodbye.")

if __name__ == "__main__":
    main()
