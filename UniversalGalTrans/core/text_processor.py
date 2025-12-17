import os
import re
import time
import threading

class TextProcessor:
    def __init__(self, glossary_path=None, debounce_time=0.1):
        self.glossary = {}
        if glossary_path and os.path.exists(glossary_path):
            self.load_glossary(glossary_path)

        self.history = [] # List of {'original': str, 'translated': str}

        # Debounce logic
        self.debounce_time = debounce_time
        self._buffer = ""
        self._timer = None
        self._lock = threading.Lock()

    def load_glossary(self, path):
        """Load glossary from a text file (Japanese=Chinese)."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        self.glossary[k.strip()] = v.strip()
        except Exception as e:
            print(f"Error loading glossary: {e}")

    def add_to_history(self, original, translated):
        """Add a translation pair to history."""
        self.history.append({'original': original, 'translated': translated})
        if len(self.history) > 20: # Keep memory efficient
            self.history.pop(0)

    def update_latest_translation(self, text_chunk):
        """Append text to the latest translation entry (Streaming support)."""
        if self.history:
            self.history[-1]['translated'] += text_chunk

    def get_history(self):
        return self.history

    def get_glossary(self):
        return self.glossary

    # --- Robustness Features ---

    def process_input_stream(self, partial_text, callback):
        """
        Thread-safe debouncer.
        Collects fragmented text (e.g., 'K', 'o', 'n', 'n', 'i'...) and calls 'callback(full_text)'
        only after silence for `debounce_time` seconds.
        """
        with self._lock:
            self._buffer += partial_text

            if self._timer:
                self._timer.cancel()

            self._timer = threading.Timer(self.debounce_time, self._flush_buffer, args=[callback])
            self._timer.start()

    def _flush_buffer(self, callback):
        with self._lock:
            full_text = self._buffer
            self._buffer = "" # Reset

        if self.is_garbage(full_text):
            print(f"[Filter] Ignored garbage: {full_text}")
            return

        callback(full_text)

    def is_garbage(self, text):
        """Simple filter to ignore system logs/filenames."""
        text = text.strip()
        if len(text) < 2: return True
        # Ignore if strictly alphanumeric (likely code/filename, not Japanese dialogue)
        if re.match(r'^[a-zA-Z0-9_./\\]+$', text):
            return True
        return False

    def protect_control_codes(self, text):
        """Replace %s, \n, etc. with placeholders."""
        placeholders = {}

        # Regex for common control codes: %s, %d, \n, [color=...]
        pattern = r'(%[sd]|\\n|\[.*?\])'
        matches = re.findall(pattern, text)

        protected_text = text
        for i, match in enumerate(matches):
            key = f"[[VAR_{i}]]"
            placeholders[key] = match
            protected_text = protected_text.replace(match, key, 1)

        return protected_text, placeholders

    def restore_control_codes(self, text, placeholders):
        """Restore placeholders to original control codes."""
        for key, val in placeholders.items():
            text = text.replace(key, val)
        return text
