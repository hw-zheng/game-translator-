# Changelog

## [Unreleased] - 2025-05-22

### Added
- **Unified Launcher (`launcher.py`)**: A single script to launch and monitor both the Bridge Server and Overlay UI subprocesses. Handles clean shutdown.
- **Logging System (`core/logger.py`)**: Centralized logging to console and `UniversalGalTrans.log`. Replaced all `print()` statements for better debugging.
- **Example Glossary (`glossary.txt`)**: Added a template for character name mapping.
- **Build Update**: `scripts/build_release.py` now packages the Launcher, Logger, and Glossary correctly. `Start.bat` now points to the python launcher.

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
