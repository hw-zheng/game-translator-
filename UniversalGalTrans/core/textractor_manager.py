import os
import requests
import zipfile
import shutil
import sys

# Force absolute import path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../../'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from UniversalGalTrans.core.logger import setup_logger

logger = setup_logger("UGT_Textractor")

TEXTRACTOR_URL = "https://github.com/Artikash/Textractor/releases/download/v5.2.0/Textractor-v5.2.0.zip"
# Note: GitHub releases often redirect. v5.2.0 is a stable known version.
# For simplicity, we hardcode a reliable version, or we could query API.

class TextractorManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.textractor_dir = os.path.join(base_path, "Textractor")
        self.exe_path = os.path.join(self.textractor_dir, "x64", "Textractor.exe")
        # Note: Textractor structure varies. Usually x86/x64 folder.

    def is_installed(self):
        return os.path.exists(self.exe_path)

    def download_and_install(self):
        logger.info("Downloading Textractor...")
        zip_path = os.path.join(self.base_path, "Textractor.zip")

        try:
            # Download
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            response = requests.get(TEXTRACTOR_URL, headers=headers, stream=True)
            if response.status_code == 200:
                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
            else:
                logger.error(f"Failed to download Textractor. Status: {response.status_code}")
                return False

            # Extract
            logger.info("Extracting Textractor...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.textractor_dir)

            # Cleanup
            os.remove(zip_path)

            # Verify extraction (Find exe location)
            self._locate_exe()

            logger.info("Textractor installed successfully.")
            return True
        except Exception as e:
            logger.error(f"Error installing Textractor: {e}")
            return False

    def _locate_exe(self):
        """Update exe_path if it's in a subdir or root."""
        possible_paths = [
            os.path.join(self.textractor_dir, "Textractor.exe"),
            os.path.join(self.textractor_dir, "x64", "Textractor.exe"),
            os.path.join(self.textractor_dir, "x86", "Textractor.exe")
        ]
        for p in possible_paths:
            if os.path.exists(p):
                self.exe_path = p
                return

    def install_extension(self):
        """Writes the Lua hook script to the extension folder."""
        # Find extension dir
        # If exe is in Textractor/x64/Textractor.exe, extensions might be in Textractor/x64/extensions/ ??
        # Or Textractor/extensions/ ?
        # Textractor usually has extensions folder next to the exe or in root.

        # We assume standard structure relative to EXE
        ext_dir = os.path.join(os.path.dirname(self.exe_path), "extensions")
        if not os.path.exists(ext_dir):
            # Try looking one level up if x64
            up_one = os.path.join(os.path.dirname(os.path.dirname(self.exe_path)), "extensions")
            if os.path.exists(up_one):
                ext_dir = up_one
            else:
                os.makedirs(ext_dir, exist_ok=True)

        logger.info(f"Installing extension to {ext_dir}...")

        lua_content = """-- Lua extension for UniversalGalTrans (Async Mode)
function ProcessSentence(sentence, sentenceInfo)
    if string.len(sentence) < 2 then return sentence end
    local http = require("socket.http")
    local ltn12 = require("ltn12")
    local body = '{"text": "' .. escape_json(sentence) .. '"}'

    -- Fire and forget (short timeout logic usually handled by library or server speed)
    http.request{
        url = "http://localhost:5000/translate",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = string.len(body)
        },
        source = ltn12.source.string(body)
    }
    return sentence
end

function escape_json(s)
    s = string.gsub(s, '\\\\', '\\\\\\\\')
    s = string.gsub(s, '"', '\\\\"')
    return s
end
"""
        with open(os.path.join(ext_dir, "ugt_hook.lua"), "w", encoding='utf-8') as f:
            f.write(lua_content)

    def launch(self):
        if not self.is_installed():
            self._locate_exe() # try finding it again
            if not self.is_installed():
                logger.error("Textractor executable not found.")
                return None

        logger.info(f"Launching Textractor from {self.exe_path}...")
        return subprocess.Popen([self.exe_path], cwd=os.path.dirname(self.exe_path))

if __name__ == "__main__":
    # Test
    mgr = TextractorManager(".")
    # mgr.download_and_install() # Commented out for dev
    if mgr.is_installed():
        print(f"Found at {mgr.exe_path}")
