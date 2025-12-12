from flask import Flask, request, jsonify
import sys
import os
import threading

# Ensure we can import core modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from UniversalGalTrans.core.llm_client import LLMClient
from UniversalGalTrans.core.database import TranslationDatabase
from UniversalGalTrans.core.text_processor import TextProcessor

app = Flask(__name__)

# Initialize Core Components
# In a real app, these config values should come from config.ini or env vars
api_key = os.environ.get("OPENAI_API_KEY", "sk-mock-key")
base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")

client = LLMClient(api_key=api_key, base_url=base_url)
db = TranslationDatabase("trans_cache.sqlite")
processor = TextProcessor(debounce_time=0.1)

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "model": client.model})

@app.route('/translate', methods=['POST'])
def translate_endpoint():
    """
    Endpoint to receive text from Hook.
    Expected JSON: {"text": "Japanese text", "context": "optional context info"}
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    raw_text = data['text']

    # 1. Immediate filtering (Garbage Check)
    if processor.is_garbage(raw_text):
        print(f"[Bridge] Filtered garbage: {raw_text}")
        return jsonify({"original": raw_text, "translated": raw_text, "status": "filtered"})

    # 2. Protect Control Codes
    protected_text, placeholders = processor.protect_control_codes(raw_text)

    # 3. Check Cache
    cached = db.get_translation(protected_text)
    if cached:
        final_text = processor.restore_control_codes(cached, placeholders)
        print(f"[Bridge] Cache Hit: {raw_text[:10]}... -> {final_text[:10]}...")
        processor.add_to_history(raw_text, final_text)
        return jsonify({"original": raw_text, "translated": final_text, "source": "cache"})

    # 4. Debounce Logic via HTTP?
    # Issue: HTTP is request-response. We can't easily "hold" the request for debouncing without timeout risks.
    # Hybrid Approach: The Hook should ideally handle fragmentation locally (Textractor has regex hooks).
    # But if we rely on our Debouncer, we might need to use a 'Job ID' approach or simple blocking if the timeout is short (0.1s).
    # For now, we assume the input is RELATIVELY complete or we accept blocking for 0.1s.

    # Let's try a synchronous wait for the debouncer for simplicity in this MVP.
    # In a production async server (FastAPI), this would be cleaner.

    # For MVP: We skip the complex threaded debouncer here and assume the Hook sends reasonably sane chunks,
    # OR we just translate what we get (risk of fragmentation).
    # To use the debouncer effectively, we'd need a WebSocket.
    # Let's stick to direct translation for the REST API for now, but keep the Processor's history.

    if api_key == "sk-mock-key":
        translated_text = f"[Simulated] {protected_text}"
    else:
        translated_text = client.translate(
            protected_text,
            history=processor.get_history(),
            glossary=processor.get_glossary()
        )

    final_text = processor.restore_control_codes(translated_text, placeholders)

    # 5. Save & Return
    if not final_text.startswith("[Error"):
        db.save_translation(protected_text, translated_text)
        processor.add_to_history(raw_text, final_text)

    print(f"[Bridge] API Trans: {raw_text[:10]}... -> {final_text[:10]}...")
    return jsonify({"original": raw_text, "translated": final_text, "source": "api"})

if __name__ == '__main__':
    print("=== Universal Galgame Translation Bridge ===")
    print("Listening on http://localhost:5000")
    app.run(port=5000, debug=False)
