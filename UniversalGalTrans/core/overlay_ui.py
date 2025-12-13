import tkinter as tk
import threading
import time
import requests
import sys

class SubtitleOverlay:
    def __init__(self, check_interval=100):
        self.root = tk.Tk()
        self.check_interval = check_interval
        self.last_text = ""
        self.server_url = "http://localhost:5000/latest"

        # Configure Window
        self.root.title("Universal Galgame Translator Overlay")
        self.root.geometry("800x150+100+600") # Default bottom position
        self.root.attributes("-topmost", True) # Always on top

        # Style: Transparent background?
        # Note: Tkinter transparency is tricky cross-platform.
        # Windows supports '-transparentcolor'.
        if sys.platform == "win32":
            self.root.attributes("-alpha", 0.8) # Semi-transparent overall
            # self.root.attributes("-transparentcolor", "black")
        else:
            self.root.attributes("-alpha", 0.8)

        self.root.configure(bg='black')

        # Label for Text
        self.label = tk.Label(
            self.root,
            text="Waiting for game text...",
            font=("Microsoft YaHei", 16, "bold"),
            fg="white",
            bg="black",
            wraplength=780,
            justify="center"
        )
        self.label.pack(expand=True, fill='both', padx=10, pady=10)

        # Start Polling Thread
        # Note: Tkinter is not thread-safe, so we use .after() loop in main thread
        self.poll_server()

    def poll_server(self):
        """Fetch latest translation from Bridge Server."""
        def fetch():
            try:
                resp = requests.get(self.server_url, timeout=0.5)
                if resp.status_code == 200:
                    data = resp.json()
                    translated = data.get("translated", "")
                    # Update UI in main thread if changed
                    if translated and translated != self.last_text:
                        self.last_text = translated
                        self.update_ui(translated)
            except Exception:
                pass # Ignore connection errors (server might be down)

            # Schedule next poll
            self.root.after(self.check_interval, self.poll_server)

        # Run fetch in a separate thread to avoid blocking UI during request?
        # Actually requests.get is blocking. So yes, we should run it in a thread,
        # but since we need to schedule the NEXT poll, it's complex.
        # For simplicity in this version, we run it directly but with short timeout.
        # If it blocks UI, we can optimize later.

        threading.Thread(target=fetch, daemon=True).start()

    def update_ui(self, text):
        """Update the label text (Must be called from main thread ideally, but Tkinter is loose)."""
        # Strictly speaking, we should use a queue or after_idle, but simple set often works.
        # Let's use after() to be safe.
        self.root.after(0, lambda: self.label.config(text=text))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    overlay = SubtitleOverlay()
    overlay.run()
