# Universal Galgame AI Translator (Core)

Based on the [Design Document](AI_Galgame_Translator_Design.md), this is the Python-based core for the Universal AI Galgame Translator.

## Features

*   **Engine Agnostic**: Designed to work with text extracted from *any* game engine (via Hooking).
*   **AI Powered**: Uses OpenAI-compatible APIs (OpenAI, Claude, DeepSeek, local LLMs).
*   **Smart Context**: Maintains translation history to understand context (e.g., pronouns).
*   **Caching**: Stores translations in a local SQLite database to save costs and speed up replay.
*   **Glossary Support**: Supports custom glossaries for consistent character names and terminology.

## Project Structure

```
UniversalGalTrans/
├── core/
│   ├── llm_client.py       # API Client (OpenAI compatible)
│   ├── database.py         # SQLite Storage for caching
│   └── text_processor.py   # History & Glossary management
├── tests/                  # Unit tests
└── requirements.txt        # Dependencies
main_cli.py                 # CLI Demo / Entry point
AI_Galgame_Translator_Design.md # Architecture Documentation
```

## Quick Start

1.  **Install Dependencies**:
    ```bash
    pip install -r UniversalGalTrans/requirements.txt
    ```

2.  **Configuration**:
    Set your API key via environment variable:
    ```bash
    export OPENAI_API_KEY="sk-your-api-key"
    # Optional: Change base URL for other providers (e.g. DeepSeek, LocalAI)
    export OPENAI_BASE_URL="https://api.deepseek.com/v1"
    ```

3.  **Run Demo**:
    ```bash
    python3 main_cli.py
    ```
    This runs a simulation showing how text is "hooked", checked against the cache, and translated via the API.

## Integration Plan (Next Steps)

To build the full "Packed" solution described in the design:

1.  **Hooking**: Integrate **Textractor** (C++) to capture real game text.
2.  **Bridge**: Use Textractor's extension interface (Lua/Python) to send text to this Python Core.
3.  **Overlay**: Display the translated text back in the game window (using D3D hooking) or in a separate window.
