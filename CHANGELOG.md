# Changelog

## [Unreleased] - 2025-05-22

### Added
- **Overlay UI (`core/overlay_ui.py`)**: A transparent, always-on-top window to display translations asynchronously. This resolves the Shift-JIS encoding issues by bypassing game memory injection.
- **Asynchronous Bridge Server**: Refactored `bridge_server.py` to be non-blocking. The `/translate` endpoint now returns `202 Accepted` immediately and offloads processing to a background thread.
- **Worker Thread with Debouncer**: The background worker now correctly integrates `TextProcessor.process_input_stream`, ensuring that text fragmentation (Risk 1.1) is handled before translation.
- **Async Hook Integration**: Updated `HOOK_INTEGRATION.md` to use a "Fire-and-Forget" Lua script that does *not* modify game memory, preventing game freezes (Risk 2).
- **Integration Tests**: Updated `tests/test_server_integration.py` and `tests/test_overlay_integration.py` to verify the async workflow.

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
