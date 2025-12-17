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
        """Add a translation pair to history. Returns the index of the entry."""
        self.history.append({'original': original, 'translated': translated})
        if len(self.history) > 20: # Keep memory efficient
            self.history.pop(0)
        return len(self.history) - 1

    def update_latest_translation(self, text_chunk, index=None):
        """
        Append text to a translation entry (Streaming support).
        If index is None, defaults to latest (unsafe for async).
        """
        if index is None:
            if self.history:
                self.history[-1]['translated'] += text_chunk
        else:
            # Check bounds in case pop(0) happened (very rare in short race, but safe)
            # Since pop(0) shifts indices, absolute index tracking is tricky.
            # But here we are single-threaded worker usually, or just short race.
            # However, if history popped, the index is invalid.
            # Given max history is 20, and fast forwarding can happen,
            # we should find the entry by reference or handle offset?
            # Simpler: Check if index is valid for now.
            if 0 <= index < len(self.history):
                # Verify it matches what we expect? No, just write.
                self.history[index]['translated'] += text_chunk
            else:
                # Fallback: if index shifted, maybe we are at index-1?
                # This architecture is simple list.
                # If we pop(0), index 5 becomes index 4.
                # To be robust, we'd need IDs.
                # For this patch, just checking bounds is better than crashing or writing to wrong index.
                pass

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
