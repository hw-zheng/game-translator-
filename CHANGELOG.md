# Changelog

## [Unreleased] - 2025-05-22

### Added
- **Textractor Automation**: Integrated `TextractorManager` into `launcher.py` to automatically download, install, and configure Textractor.
    - Added `UniversalGalTrans/core/textractor_manager.py` to handle ZIP downloads from GitHub and Lua script injection.
    - Updated `launcher.py` to spawn Textractor alongside the core services.
- **Multi-Provider Support**: Refactored `llm_client.py` to support `gemini`, `deepseek`, and `qwen` (via OpenAI compatibility or adapters).
- **Setup Wizard**: Added a graphical (Tkinter) Setup Wizard in `launcher.py` that prompts the user for their API Key and Provider on first run.
- **Robust Path Handling**: Fixed import errors in `launcher.py`, `bridge_server.py`, and `overlay_ui.py` to ensuring reliable execution from the distribution folder.

### Fixed
- **Launcher Path Error**: Fixed `ModuleNotFoundError` when running `launcher.py` (via `Start.bat`) by forcing the package root directory into `sys.path`.

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
