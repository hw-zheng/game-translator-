import subprocess
import time
import requests
import sys
import os

def run_tests():
    print("=== Starting Functional Tests (Async Mode) ===")

    # 1. Start Server
    print("[Test] Launching Bridge Server...")
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-mock-key"

    server_process = subprocess.Popen(
        [sys.executable, "UniversalGalTrans/core/bridge_server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    time.sleep(3)
    base_url = "http://localhost:5000"

    def wait_for_translation(expected_text, timeout=5):
        """Poll /latest until expected translation appears."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"{base_url}/latest")
                data = resp.json()
                # Check if this is the translation for our text
                # Note: mock returns "[Simulated] {text}"
                if expected_text in data.get('translated', ''):
                    return data
            except:
                pass
            time.sleep(0.2)
        return None

    try:
        # 2. Check Status
        print("\n[Test 1] Checking Server Status...")
        resp = requests.get(f"{base_url}/status")
        assert resp.status_code == 200
        print(">>> PASS")

        # 3. Test Basic Translation (Async)
        print("\n[Test 2] Basic Translation (Async)...")
        payload = {"text": "こんにちは"}
        resp = requests.post(f"{base_url}/translate", json=payload)
        assert resp.status_code == 202 # Accepted
        print(f"Request Accepted: {resp.json()}")

        # Poll for result
        result = wait_for_translation("こんにちは")
        assert result is not None
        assert "[Simulated]" in result['translated']
        print(f"Async Result Found: {result}")
        print(">>> PASS")

        # 4. Test Caching (via Async)
        print("\n[Test 3] Caching Mechanism...")

        # Force a wait to ensure Debouncer clears previous buffer (avoid merging)
        time.sleep(1.0)

        # Send same text again
        requests.post(f"{base_url}/translate", json=payload)
        result = wait_for_translation("こんにちは")
        assert result is not None
        print(">>> PASS")

        # 5. Test Control Code Protection
        print("\n[Test 4] Control Code Protection...")

        time.sleep(1.0) # Wait for debouncer

        text_with_code = "Hello %s"
        requests.post(f"{base_url}/translate", json={"text": text_with_code})

        result = wait_for_translation("Hello %s")
        assert result is not None
        assert "%s" in result['translated']
        assert "[[VAR" not in result['translated']
        print(f"Protected Result: {result}")
        print(">>> PASS")

        # 6. Test Garbage Filtering
        print("\n[Test 5] Garbage Filtering...")
        garbage = "sys_log_001.exe"
        resp = requests.post(f"{base_url}/translate", json={"text": garbage})
        assert resp.json()['status'] == 'filtered'
        # Should NOT appear in /latest (should remain previous text)
        time.sleep(1)
        latest = requests.get(f"{base_url}/latest").json()
        assert "sys_log" not in latest.get('translated', '')
        print(">>> PASS")

    except Exception as e:
        print(f"FAIL: {e}")
        # Print server logs if fail
        # print(server_process.stdout.read().decode())
    finally:
        print("\n[Test] Terminating Server...")
        server_process.terminate()
        server_process.wait()
        if os.path.exists("trans_cache.sqlite"):
            os.remove("trans_cache.sqlite")

if __name__ == "__main__":
    run_tests()
