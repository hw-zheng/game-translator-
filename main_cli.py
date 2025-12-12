import os
import sys

# Ensure the core module is in the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'UniversalGalTrans'))

from UniversalGalTrans.core.llm_client import LLMClient
from UniversalGalTrans.core.database import TranslationDatabase
from UniversalGalTrans.core.text_processor import TextProcessor

def main():
    print("=== Universal Galgame Translator Core (CLI Demo) ===")

    # 1. Configuration (Mocking User Input)
    api_key = os.environ.get("OPENAI_API_KEY", "sk-mock-key") # Use env var or mock
    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

    if api_key == "sk-mock-key":
        print("Warning: No API Key found. Translations will likely fail or require a mock server.")
        print("Set OPENAI_API_KEY environment variable to test with real API.")

    # 2. Initialize Modules
    client = LLMClient(api_key=api_key, base_url=base_url)
    db = TranslationDatabase("test_db.sqlite")
    processor = TextProcessor()

    # 3. Mock Text Stream (Simulating Textractor Hook)
    game_texts = [
        "おはようございます。",
        "今日はいい天気ですね。",
        "先輩、一緒に帰りませんか？"
    ]

    print(f"\n[System] Loaded {len(game_texts)} lines from mock hook.")

    for original_text in game_texts:
        print(f"\n>>> Hooked: {original_text}")

        # Check Cache
        cached = db.get_translation(original_text)
        if cached:
            print(f"    [Cache] {cached}")
            processor.add_to_history(original_text, cached)
            continue

        # Translate via API
        # Note: In a real run without a valid key, this will print an Error message.
        # For this demo, if the key is mock, we might want to simulate a response to show flow.
        if api_key == "sk-mock-key":
             # Simulating API response for demo purposes
             import time
             time.sleep(0.5)
             translated_text = f"[Simulated Translation] {original_text} (CN)"
        else:
             translated_text = client.translate(
                 original_text,
                 history=processor.get_history(),
                 glossary=processor.get_glossary()
            )

        print(f"    [API]   {translated_text}")

        # Save to Cache and History
        if not translated_text.startswith("[Error"):
            db.save_translation(original_text, translated_text, model="demo-model")
            processor.add_to_history(original_text, translated_text)

    print("\n=== Demo Complete ===")
    print("Check 'test_db.sqlite' for cached translations.")

if __name__ == "__main__":
    main()
