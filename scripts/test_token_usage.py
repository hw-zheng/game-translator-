import requests
import time
import json

SERVER_URL = "http://localhost:5000"

def send_text(text):
    print(f"Sending: {text}")
    try:
        resp = requests.post(f"{SERVER_URL}/translate", json={"text": text}, timeout=1)
        print(f"Status: {resp.status_code} ({resp.json()})")
    except Exception as e:
        print(f"Request failed: {e}")

def get_latest():
    try:
        resp = requests.get(f"{SERVER_URL}/latest", timeout=1)
        data = resp.json()
        print(f"Latest: [{data.get('original')}] -> [{data.get('translated')}]")
        return data.get('original'), data.get('translated')
    except Exception as e:
        print(f"Check failed: {e}")
        return None, None

def run_test():
    print("=== Testing Token Optimization ===")

    # 1. New Sentence
    s1 = "こんにちは、世界。"
    send_text(s1)
    time.sleep(1) # Wait for processing
    get_latest()

    # 2. Duplicate Sentence (Immediate Spam)
    print("\n[Test] Sending duplicate sentence immediately...")
    send_text(s1)
    time.sleep(1)
    get_latest()

    # 3. New Sentence 2
    s2 = "これはテストです。"
    print("\n[Test] Sending new sentence...")
    send_text(s2)
    time.sleep(1) # Wait for processing
    get_latest()

    print("\nCheck the 'UGT_Server.log'. You should see:")
    print("1. 'Processing finalized text' for the first sentence.")
    print("2. 'Duplicate text ignored' for the second sentence.")
    print("3. 'Processing finalized text' for the third sentence.")

if __name__ == "__main__":
    run_test()
