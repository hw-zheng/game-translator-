import sqlite3
import hashlib
import json
import os

class TranslationDatabase:
    def __init__(self, db_path="trans_cache.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS translations (
                hash TEXT PRIMARY KEY,
                original TEXT,
                translated TEXT,
                model TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def get_hash(self, text):
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def get_translation(self, text):
        """Retrieve translation from cache if it exists."""
        text_hash = self.get_hash(text)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT translated FROM translations WHERE hash=?", (text_hash,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def save_translation(self, text, translated_text, model="unknown"):
        """Save translation to cache."""
        text_hash = self.get_hash(text)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO translations (hash, original, translated, model) VALUES (?, ?, ?, ?)",
                (text_hash, text, translated_text, model)
            )
            conn.commit()
        except Exception as e:
            print(f"Error saving to DB: {e}")
        finally:
            conn.close()
