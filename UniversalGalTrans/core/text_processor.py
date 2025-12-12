import os

class TextProcessor:
    def __init__(self, glossary_path=None):
        self.glossary = {}
        if glossary_path and os.path.exists(glossary_path):
            self.load_glossary(glossary_path)

        self.history = [] # List of {'original': str, 'translated': str}

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

    def get_history(self):
        return self.history

    def get_glossary(self):
        return self.glossary
