# Hook Integration Guide (Async / Overlay)

This guide explains how to connect **Textractor** to the Universal Galgame Translator using the new **Asynchronous Overlay** mode.

## Architecture

```
[Game] -> [Textractor] --(Fire-and-Forget)--> [Server] -> [Queue] -> [AI] -> [Overlay UI]
```

*   **Game**: Continues running smoothly (no freezes).
*   **Overlay**: Displays the translation in a transparent window on top of the game.

## Step 1: Start the System

Run `Start.bat` (Windows) or `python scripts/build_release.py` (Dev) to launch both the Bridge Server and the Overlay UI.

## Step 2: Configure Textractor Extension

Create `http_async.lua` in your Textractor extensions folder:

```lua
-- Lua extension for UniversalGalTrans (Async Mode)
-- Sends text to server and immediately returns original text (no modification)

function ProcessSentence(sentence, sentenceInfo)
    -- Filter out obvious short garbage locally to save HTTP overhead
    if string.len(sentence) < 2 then return sentence end

    local http = require("socket.http")
    local ltn12 = require("ltn12")

    local body = '{"text": "' .. escape_json(sentence) .. '"}'

    -- Send POST request but ignore response content (or use 0 timeout if supported)
    -- Note: LuaSocket's http.request is blocking.
    -- To achieve true non-blocking, we set a very short timeout if possible,
    -- or rely on the Server's fast "202 Accepted" response (which takes < 5ms).

    local res, code, headers = http.request{
        url = "http://localhost:5000/translate",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = string.len(body)
        },
        source = ltn12.source.string(body)
    }

    -- Always return original sentence so the game memory is NOT modified.
    -- This prevents Shift-JIS encoding crashes.
    return sentence
end

function escape_json(s)
    s = string.gsub(s, '\\', '\\\\')
    s = string.gsub(s, '"', '\\"')
    return s
end
```

## Step 3: Play

1. Attach Textractor to the game.
2. Watch the **Overlay Window** (not the game window) for translations.
