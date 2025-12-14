import sys
import os
import subprocess
import time
import signal
import threading

# Add root to path (parent of this script) - Force absolute path and insert at beginning
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from UniversalGalTrans.core.logger import setup_logger
from UniversalGalTrans.core.config import get_config
from UniversalGalTrans.core.textractor_manager import TextractorManager
import tkinter as tk
from tkinter import simpledialog, messagebox

logger = setup_logger("UGT_Launcher")

def setup_wizard(cfg):
    """Simple UI to ask for API Key if missing."""
    api_key = cfg.get("General", "OPENAI_API_KEY")

    # Check for empty or placeholder keys
    if not api_key or api_key in ["sk-mock-key", "sk-your-key-here"]:
        logger.info("Setup Wizard: No valid API Key found. Launching setup dialog...")
        try:
            root = tk.Tk()
            root.withdraw() # Hide main window
        except Exception as e:
            logger.error(f"Cannot initialize Tkinter: {e}")
            return

        # Ask Provider
        # Simple implementation: Just ask for Key and Base URL
        msg = "Welcome! Please configure your AI Provider.\n\n"

        key = simpledialog.askstring("Setup", msg + "Enter API Key (OpenAI/DeepSeek/Qwen):")
        if key:
            cfg.config["General"]["OPENAI_API_KEY"] = key

            # Optional Base URL
            base = simpledialog.askstring("Setup", "Enter Base URL (Leave empty for OpenAI):")
            if base:
                cfg.config["General"]["OPENAI_BASE_URL"] = base
            else:
                 cfg.config["General"]["OPENAI_BASE_URL"] = "https://api.openai.com/v1"

            # Provider Hint
            # We could ask, but let's default to openai since we use compatible endpoint
            cfg.config["General"]["PROVIDER"] = "openai"

            # Save
            with open("config.ini", "w") as f:
                cfg.config.write(f)
        root.destroy()

def main():
    logger.info("=== Universal Galgame Translator Launcher ===")

    # 0. Setup Wizard
    cfg = get_config()
    try:
        setup_wizard(cfg)
    except Exception as e:
        logger.error(f"Setup Wizard failed (GUI environment missing?): {e}")

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

    # 3. Manage Textractor (Auto-Install & Launch)
    tm = TextractorManager(os.getcwd())
    textractor_process = None

    if not tm.is_installed():
        logger.info("Textractor not found. Attempting to download...")
        # Since we might be in GUI mode, maybe ask user? For now auto-download.
        if tm.download_and_install():
            tm.install_extension()
    else:
        # Ensure hook is always up to date
        tm.install_extension()

    if tm.is_installed():
        logger.info("Launching Textractor...")
        try:
            textractor_process = tm.launch()
        except Exception as e:
            logger.error(f"Failed to launch Textractor: {e}")
    else:
        logger.warning("Textractor could not be installed. Please install manually.")

    # 4. Monitor Loop
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

        # We generally don't kill Textractor as user might want to keep playing?
        # But if it's a unified tool, maybe we should?
        # Let's leave Textractor running or kill it based on preference.
        # Currently leaving it running.

        logger.info("Goodbye.")

if __name__ == "__main__":
    main()
