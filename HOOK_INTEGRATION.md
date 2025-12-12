# Hook Integration Guide

This guide explains how to connect existing Text Hooks (specifically **Textractor**) to the Universal Galgame Translator.

## Architecture

```
[Game Process] -> [Textractor (Hook)] -> [Extension Script] --(HTTP)--> [Bridge Server] -> [AI Core]
```

## Step 1: Start the Bridge Server

Run the `Start.bat` included in the release package, or manually run:
```bash
python UniversalGalTrans/core/bridge_server.py
```
Ensure it says "Listening on http://localhost:5000".

## Step 2: Configure Textractor

You need to add an extension to Textractor that forwards text to our server.

1.  Open your **Textractor** folder.
2.  Navigate to the `extensions` folder (if it exists, or create a script in Lua/Python if supported).
    *   *Note: Recent Textractor versions support Lua extensions.*
3.  Create a file named `http_sender.lua` (example) with the following content:

```lua
-- Lua extension for Textractor to send text to UniversalGalTrans
-- Place this in the Textractor extensions folder

function ProcessSentence(sentence, sentenceInfo)
    -- Filter out short garbage
    if string.len(sentence) < 2 then return sentence end

    -- Send to Python Server
    local http = require("socket.http") -- Requires LuaSocket
    local ltn12 = require("ltn12")

    local body = '{"text": "' .. escape_json(sentence) .. '"}'
    local response_body = {}

    local res, code, response_headers = http.request{
        url = "http://localhost:5000/translate",
        method = "POST",
        headers = {
            ["Content-Type"] = "application/json",
            ["Content-Length"] = string.len(body)
        },
        source = ltn12.source.string(body),
        sink = ltn12.sink.table(response_body)
    }

    if code == 200 then
        -- Parse JSON response (naive match for simplicity)
        local resp_str = table.concat(response_body)
        local translation = resp_str:match('"translated":%s*"(.-)"')
        if translation then
            return translation -- Replace text in Textractor
        end
    end

    return sentence
end

function escape_json(s)
    s = string.gsub(s, '\\', '\\\\')
    s = string.gsub(s, '"', '\\"')
    return s
end
```

*Note: The above Lua script is a conceptual example. Textractor's extension API may vary.*

## Step 3: Attach to Game

1.  Open Textractor.
2.  Attach to your game.
3.  Ensure your `http_sender` extension is loaded and active.
4.  Play the game. Text should be sent to the Python window, translated, and displayed back in Textractor.
