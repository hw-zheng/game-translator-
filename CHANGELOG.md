# Changelog

## [Unreleased] - 2025-05-22

### Added
- **Configuration Manager (`core/config.py`)**: Centralized settings management reading from `config.ini`. Replaces environment variables for API keys and Server settings.
- **Enhanced Overlay UI**:
    - **Frameless Window**: Removed standard OS title bar for a true subtitle look.
    - **Draggable**: Implemented mouse drag support to move the subtitle strip freely.
    - **Customizable**: Font size, color, background, opacity, and window size are now configurable via `config.ini`.
- **Refactored Server**: `bridge_server.py` now reads Host/Port and API keys from `config.ini`.
- **Packaging Update**: `scripts/build_release.py` now includes a full `config.ini` template with Display settings.

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
