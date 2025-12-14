import tkinter as tk
import threading
import time
import requests
import sys
import os
# Ensure config can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from UniversalGalTrans.core.config import get_config
from UniversalGalTrans.core.logger import setup_logger

logger = setup_logger("UGT_UI")

class SubtitleOverlay:
    def __init__(self):
        self.cfg = get_config()
        self.check_interval = 100
        self.last_text = ""

        host = self.cfg.get("Server", "HOST", "localhost")
        port = self.cfg.get("Server", "PORT", "5000")
        self.server_url = f"http://{host}:{port}/latest"

        # Load UI Settings
        self.width = self.cfg.get_int("Display", "WINDOW_WIDTH", 800)
        self.height = self.cfg.get_int("Display", "WINDOW_HEIGHT", 150)
        self.x_pos = self.cfg.get_int("Display", "X_POS", 100)
        self.y_pos = self.cfg.get_int("Display", "Y_POS", 600)

        self.bg_color = self.cfg.get("Display", "BG_COLOR", "black")
        self.fg_color = self.cfg.get("Display", "TEXT_COLOR", "white")
        self.font_family = self.cfg.get("Display", "FONT_FAMILY", "Microsoft YaHei")
        self.font_size = self.cfg.get_int("Display", "FONT_SIZE", 16)
        self.opacity = self.cfg.get_float("Display", "OPACITY", 0.8)

        # Setup Window
        self.root = tk.Tk()
        self.root.title("Universal Galgame Translator Overlay")
        self.root.geometry(f"{self.width}x{self.height}+{self.x_pos}+{self.y_pos}")

        # Frameless and Topmost
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)

        # Opacity
        if sys.platform == "win32":
            self.root.attributes("-alpha", self.opacity)
        else:
            self.root.attributes("-alpha", self.opacity)

        self.root.configure(bg=self.bg_color)

        # Drag Logic
        self._drag_data = {"x": 0, "y": 0}
        self.root.bind("<Button-1>", self.start_drag)
        self.root.bind("<B1-Motion>", self.do_drag)

        # Close on Right Click
        self.root.bind("<Button-3>", lambda e: self.root.quit())

        # Label for Text
        self.label = tk.Label(
            self.root,
            text="Waiting for game text... (Drag to move, Right-click to exit)",
            font=(self.font_family, self.font_size, "bold"),
            fg=self.fg_color,
            bg=self.bg_color,
            wraplength=self.width - 20,
            justify="center"
        )
        self.label.pack(expand=True, fill='both', padx=10, pady=10)

        # Allow dragging via Label too
        self.label.bind("<Button-1>", self.start_drag)
        self.label.bind("<B1-Motion>", self.do_drag)
        self.label.bind("<Button-3>", lambda e: self.root.quit())

        self.poll_server()

    def start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def do_drag(self, event):
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + delta_x
        y = self.root.winfo_y() + delta_y
        self.root.geometry(f"+{x}+{y}")

    def poll_server(self):
        """Fetch latest translation from Bridge Server."""
        def fetch():
            try:
                resp = requests.get(self.server_url, timeout=0.5)
                if resp.status_code == 200:
                    data = resp.json()
                    translated = data.get("translated", "")
                    if translated and translated != self.last_text:
                        self.last_text = translated
                        self.update_ui(translated)
            except Exception:
                pass
            self.root.after(self.check_interval, self.poll_server)

        # Since we use .after for scheduling, we can't block.
        # But requests.get is blocking. Threading the fetch is safer.
        threading.Thread(target=fetch, daemon=True).start()

    def update_ui(self, text):
        self.root.after(0, lambda: self.label.config(text=text))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    overlay = SubtitleOverlay()
    overlay.run()
