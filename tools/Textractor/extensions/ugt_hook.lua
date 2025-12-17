-- Lua extension for UniversalGalTrans (Async Mode)
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
    s = string.gsub(s, '\\', '\\\\')
    s = string.gsub(s, '"', '\\"')
    return s
end
