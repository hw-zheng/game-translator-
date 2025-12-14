# Changelog

## [Unreleased] - 2025-05-22

### Fixed
- **Launcher Crash**: Fixed `ModuleNotFoundError` in `launcher.py` by correctly adding the parent directory to `sys.path`. This ensures the script runs correctly from `Start.bat` inside the `dist` folder.
- **Import Paths**: Verified and standardized import paths across `bridge_server.py`, `overlay_ui.py`, and `launcher.py` to support both dev and production environments.

### Added
- **README Localization**: Translated the entire documentation to Chinese, including "Quick Start" guide and architecture explanation.
- **Unified Launcher (`launcher.py`)**: A single script to launch and monitor both the Bridge Server and Overlay UI subprocesses. Handles clean shutdown.
- **Logging System (`core/logger.py`)**: Centralized logging to console and `UniversalGalTrans.log`. Replaced all `print()` statements for better debugging.
- **Configuration Manager (`core/config.py`)**: Centralized settings management reading from `config.ini`. Replaces environment variables for API keys and Server settings.
- **Enhanced Overlay UI**:
    - **Frameless Window**: Removed standard OS title bar for a true subtitle look.
    - **Draggable**: Implemented mouse drag support to move the subtitle strip freely.
    - **Customizable**: Font size, color, background, opacity, and window size are now configurable via `config.ini`.
- **Refactored Server**: `bridge_server.py` now reads Host/Port and API keys from `config.ini` and uses async processing.
- **Glossary Support**: Added `glossary.txt` template.
- **Packaging**: `scripts/build_release.py` now produces a complete distribution with launcher, config, glossary, and core.

### Test Results
**Execution Time**: 2025-05-22
**Status**: PASS

```text
=== Starting Functional Tests (Async Mode) ===
[Test] Launching Bridge Server...
[Test 1] Checking Server Status... PASS
[Test 2] Basic Translation (Async)... PASS
[Test 3] Caching Mechanism... PASS
[Test 4] Control Code Protection... PASS
[Test 5] Garbage Filtering... PASS
[Test] Terminating Server...
---
=== Starting Overlay Integration Tests (Async) ===
[Test] Launching Bridge Server...
[Test 1] Checking Empty State... PASS
[Test 2] Pushing Text to Server... PASS
[Test 3] Verifying /latest Update... PASS
[Test] Overlay Integration Logic Verified (Headless).
[Test] Terminating Server...
```
