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

    # 3. Mock Text Stream (Simulating Textractor Hook with fragmentation)
    # Simulating: "Wait for", " fragments", " to merge."
    mock_hook_events = [
        "お", "は", "よ", "う", "ご", "ざ", "い", "ま", "す", "。", # Fragmented sentence 1
        "system_log_001", # Garbage
        "先輩、", "一緒に", "帰りませんか？" # Fragmented sentence 2
    ]

    print(f"\n[System] Simulating {len(mock_hook_events)} hook events with debouncing...")

    # Define a callback to handle 'finalized' text
    def on_text_finalized(final_text):
        print(f"\n>>> [Debounced Event] Text: '{final_text}'")

        # 1. Protect Control Codes
        protected_text, placeholders = processor.protect_control_codes(final_text)
        if placeholders:
            print(f"    [Protect] Masked: {protected_text} | Map: {placeholders}")

        # 2. Check Cache
        cached = db.get_translation(protected_text)
        if cached:
            print(f"    [Cache] {processor.restore_control_codes(cached, placeholders)}")
            processor.add_to_history(final_text, cached)
            return

        # 3. Translate via API
        if api_key == "sk-mock-key":
             # Simulating API response
             translated_text = f"[Simulated] {protected_text} (CN)"
        else:
             translated_text = client.translate(
                 protected_text,
                 history=processor.get_history(),
                 glossary=processor.get_glossary()
            )

        # 4. Restore Codes
        final_translation = processor.restore_control_codes(translated_text, placeholders)
        print(f"    [API]   {final_translation}")

        # 5. Save
        if not translated_text.startswith("[Error"):
            db.save_translation(protected_text, translated_text, model="demo-model")
            processor.add_to_history(final_text, final_translation)

    # Simulate loop
    import time
    for frag in mock_hook_events:
        # Feed fragment
        processor.process_input_stream(frag, on_text_finalized)

        # Simulate delays
        if frag == "。":
            # End of sentence 1, wait longer to trigger debounce
            time.sleep(0.2)
        elif "log" in frag:
            # Garbage usually comes in bursts or separated events
            time.sleep(0.2)
        else:
            # Normal typing speed
            time.sleep(0.01)

    # Wait for debounce to finish
    time.sleep(1.0)

    print("\n=== Demo Complete ===")
    print("Check 'test_db.sqlite' for cached translations.")

if __name__ == "__main__":
    main()
