from flask import Flask, request, jsonify
import sys
import os
import threading
import queue
import time

# Ensure we can import core modules - Force absolute path and insert at beginning
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../../'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from UniversalGalTrans.core.llm_client import LLMClient
from UniversalGalTrans.core.database import TranslationDatabase
from UniversalGalTrans.core.text_processor import TextProcessor
from UniversalGalTrans.core.config import get_config
from UniversalGalTrans.core.logger import setup_logger

logger = setup_logger("UGT_Server")
app = Flask(__name__)

# Initialize Core Components via Config
cfg = get_config()
api_key = cfg.get("General", "OPENAI_API_KEY")
base_url = cfg.get("General", "OPENAI_BASE_URL")
model = cfg.get("General", "MODEL", "gpt-3.5-turbo")
provider = cfg.get("General", "PROVIDER", "openai")
debounce_time = cfg.get_float("General", "DEBOUNCE_TIME", 0.3)

client = LLMClient(api_key=api_key, base_url=base_url, model=model, provider=provider)
db = TranslationDatabase("trans_cache.sqlite")
processor = TextProcessor(debounce_time=debounce_time)

# Processing Queue for Async Handling
text_queue = queue.Queue()

# --- Background Worker ---
def worker():
    """Consumes text from queue and processes it via Debouncer -> AI."""
    logger.info("Started background processing thread.")

    def on_text_finalized(final_text):
        """Callback when debouncer decides text is complete."""
        logger.info(f"Processing finalized text: {final_text}")

        # 1. Protect Control Codes
        protected_text, placeholders = processor.protect_control_codes(final_text)

        # 2. Check Cache
        cached = db.get_translation(protected_text)
        if cached:
            final_translation = processor.restore_control_codes(cached, placeholders)
            logger.info(f"Cache Hit: {final_translation[:20]}...")
            processor.add_to_history(final_text, final_translation)
            return

        # 3. Call AI API
        if api_key == "sk-mock-key":
            # Simulate latency
            time.sleep(0.5)
            translated_text = f"[Simulated] {protected_text}"
        else:
            translated_text = client.translate(
                protected_text,
                history=processor.get_history(),
                glossary=processor.get_glossary()
            )

        # 4. Restore & Save
        final_translation = processor.restore_control_codes(translated_text, placeholders)
        if not final_translation.startswith("[Error"):
            db.save_translation(protected_text, translated_text)
            processor.add_to_history(final_text, final_translation)

        logger.info(f"Translation Ready: {final_translation[:20]}...")

    while True:
        try:
            # Block until text arrives
            raw_text = text_queue.get()
            # Feed into Debouncer (Thread-safe)
            processor.process_input_stream(raw_text, on_text_finalized)
            text_queue.task_done()
        except Exception as e:
            logger.error(f"Worker Error: {e}")

# Start the worker thread
threading.Thread(target=worker, daemon=True).start()

# --- Endpoints ---

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"status": "running", "model": client.model})

@app.route('/translate', methods=['POST'])
def translate_endpoint():
    """
    Async Endpoint. Receives text, pushes to queue, returns immediately.
    Client (Hook) does NOT wait for translation.
    """
    data = request.json
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    raw_text = data['text']

    # 1. Immediate filtering (Garbage Check) - Fast check
    if processor.is_garbage(raw_text):
        logger.info(f"Filtered garbage: {raw_text}")
        return jsonify({"status": "filtered"}), 200

    # 2. Push to Queue
    text_queue.put(raw_text)

    # 3. Return immediately (Fire-and-forget success)
    return jsonify({"status": "queued"}), 202

@app.route('/latest', methods=['GET'])
def get_latest():
    """Endpoint for Overlay UI to pull the most recent translation."""
    history = processor.get_history()
    if not history:
        return jsonify({"original": "", "translated": "Waiting for text..."})

    latest_entry = history[-1]
    return jsonify(latest_entry)

if __name__ == '__main__':
    host = cfg.get("Server", "HOST", "localhost")
    port = cfg.get_int("Server", "PORT", 5000)
    print(f"=== Universal Galgame Translation Bridge (Async) ===")
    print(f"Listening on http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
