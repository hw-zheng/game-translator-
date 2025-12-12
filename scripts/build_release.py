import os
import shutil
import zipfile

def create_dist():
    dist_dir = "dist"
    pkg_name = "UniversalGalTrans"

    # 1. Cleanup
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)

    print(f"[Build] Creating '{dist_dir}' directory...")

    # 2. Copy Python Core
    target_pkg_dir = os.path.join(dist_dir, pkg_name)
    shutil.copytree(pkg_name, target_pkg_dir, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.sqlite'))
    print("[Build] Copied Core module.")

    # 3. Create Launcher Script (Start.bat)
    # Note: In a real scenario, this would use an embedded python or assume python is in PATH.
    bat_content = """@echo off
echo Starting Universal Galgame Translator...
echo Ensure you have Python 3.8+ installed.
echo Installing dependencies...
pip install -r UniversalGalTrans/requirements.txt > nul

echo Starting Bridge Server...
start /B python UniversalGalTrans/core/bridge_server.py

echo.
echo Server is running on http://localhost:5000
echo Configure your Hook (Textractor) to send POST requests to /translate
echo.
pause
"""
    with open(os.path.join(dist_dir, "Start.bat"), "w") as f:
        f.write(bat_content)
    print("[Build] Created Start.bat")

    # 4. Copy Config Template
    config_content = """[General]
# API Configuration
OPENAI_API_KEY=sk-your-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
MODEL=gpt-3.5-turbo

[Display]
# Mode: overlay or replace (not yet implemented in Python core)
MODE=overlay
"""
    with open(os.path.join(dist_dir, "config.ini"), "w") as f:
        f.write(config_content)
    print("[Build] Created config.ini")

    # 5. Zip it (Optional)
    # shutil.make_archive("UniversalGalTrans_Patch", 'zip', dist_dir)

    print("[Build] Build complete. Output is in 'dist/' folder.")

if __name__ == "__main__":
    create_dist()
