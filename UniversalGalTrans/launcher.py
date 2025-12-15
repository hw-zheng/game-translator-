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
from UniversalGalTrans.core.llm_client import LLMClient
import tkinter as tk
from tkinter import simpledialog, messagebox

logger = setup_logger("UGT_Launcher")

def test_connection(api_key, base_url, model):
    """Try to connect to the AI service."""
    try:
        client = LLMClient(api_key=api_key, base_url=base_url, model=model)
        success, msg = client.test_connection()
        return success, msg
    except Exception as e:
        return False, str(e)

def setup_wizard(cfg):
    """UI to configure API and test connection."""
    api_key = cfg.get("General", "OPENAI_API_KEY")
    base_url = cfg.get("General", "OPENAI_BASE_URL")
    model = cfg.get("General", "MODEL", "gpt-3.5-turbo")

    # Always show setup if key is invalid, or offer a way to re-config/test?
    # For now, trigger if key is default/missing.
    if not api_key or api_key in ["sk-mock-key", "sk-your-key-here"]:
        logger.info("Setup Wizard: No valid API Key found. Launching setup dialog...")
        try:
            root = tk.Tk()
            root.withdraw() # Hide main window

            # Since simpledialog is limited, we might want a loop or just basic input
            msg = "Welcome! Please configure your AI Provider (Qwen/OpenAI/DeepSeek).\n"

            while True:
                key = simpledialog.askstring("Setup Step 1/3", msg + "\nEnter API Key:")
                if not key: return # User cancelled

                base = simpledialog.askstring("Setup Step 2/3", "Enter Base URL (e.g. https://dashscope.aliyuncs.com/compatible-mode/v1):\n(Leave empty for default OpenAI)")
                if base is None: return # User cancelled
                if not base: base = "https://api.openai.com/v1"

                # Step 3: Model Selection
                model_input = simpledialog.askstring("Setup Step 3/3", "Enter Model Name (e.g., gpt-3.5-turbo, qwen-plus, deepseek-chat):")
                if model_input is None: return # User cancelled
                if not model_input: model_input = "gpt-3.5-turbo"

                # Test Connection
                if messagebox.askyesno("Test Connection", f"Do you want to test the connection to '{model_input}' now?"):
                    success, error = test_connection(key, base, model_input)
                    if success:
                        messagebox.showinfo("Success", "Connection Verified!")
                        # Save
                        cfg.config["General"]["OPENAI_API_KEY"] = key
                        cfg.config["General"]["OPENAI_BASE_URL"] = base
                        cfg.config["General"]["MODEL"] = model_input
                        cfg.config["General"]["PROVIDER"] = "openai" # Force compatible mode
                        with open("config.ini", "w") as f:
                            cfg.config.write(f)
                        break
                    else:
                        retry = messagebox.askretrycancel("Connection Failed", f"Error: {error}\n\nCheck your Key, URL, and Model Name.")
                        if not retry:
                            break # Continue without saving or minimal save?
                        # Loop back to ask key
                else:
                     # Save without testing
                    cfg.config["General"]["OPENAI_API_KEY"] = key
                    cfg.config["General"]["OPENAI_BASE_URL"] = base
                    cfg.config["General"]["MODEL"] = model_input
                    cfg.config["General"]["PROVIDER"] = "openai"
                    with open("config.ini", "w") as f:
                        cfg.config.write(f)
                    break

            root.destroy()
        except Exception as e:
            logger.error(f"Cannot initialize Tkinter: {e}")
            return

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

    # 3. Manage Textractor (Launch Local)
    # Note: As per user request, we do NOT download. We expect it in tools/Textractor.
    tm = TextractorManager(os.getcwd())
    textractor_process = None

    if tm.is_installed():
        # Ensure hook is always up to date
        tm.install_extension()
        logger.info("Launching Textractor...")
        try:
            textractor_process = tm.launch()
        except Exception as e:
            logger.error(f"Failed to launch Textractor: {e}")
    else:
        logger.warning("Textractor executable not found! Please place 'Textractor.exe' in the 'tools/Textractor' folder.")
        # Optional: Warn user via UI
        try:
             root = tk.Tk()
             root.withdraw()
             messagebox.showwarning("Missing Component", "Textractor not found in 'tools/Textractor'.\nPlease install it manually to capture game text.")
             root.destroy()
        except: pass

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
