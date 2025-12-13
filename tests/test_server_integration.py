import subprocess
import time
import requests
import sys
import os
import signal

def run_tests():
    print("=== Starting Functional Tests ===")

    # 1. Start Server
    print("[Test] Launching Bridge Server...")
    # Set env vars for mock mode
    env = os.environ.copy()
    env["OPENAI_API_KEY"] = "sk-mock-key"

    server_process = subprocess.Popen(
        [sys.executable, "UniversalGalTrans/core/bridge_server.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(3)

    base_url = "http://localhost:5000"

    try:
        # 2. Check Status
        print("\n[Test 1] Checking Server Status...")
        try:
            resp = requests.get(f"{base_url}/status")
            print(f"Status Code: {resp.status_code}")
            print(f"Response: {resp.json()}")
            assert resp.status_code == 200
            print(">>> PASS")
        except Exception as e:
            print(f">>> FAIL: {e}")
            return

        # 3. Test Basic Translation (Mock)
        print("\n[Test 2] Basic Translation...")
        payload = {"text": "こんにちは"}
        resp = requests.post(f"{base_url}/translate", json=payload)
        data = resp.json()
        print(f"Response: {data}")
        assert data['source'] == "api"
        assert "[Simulated]" in data['translated']
        print(">>> PASS")

        # 4. Test Caching
        print("\n[Test 3] Caching Mechanism...")
        # Send same text again
        resp = requests.post(f"{base_url}/translate", json=payload)
        data = resp.json()
        print(f"Response: {data}")
        assert data['source'] == "cache"  # Should be from cache now
        assert "[Simulated]" in data['translated']
        print(">>> PASS")

        # 5. Test Control Code Protection
        print("\n[Test 4] Control Code Protection...")
        text_with_code = "Hello %s, how are you?"
        # The mock translator just prepends [Simulated], so we expect: "[Simulated] Hello [[VAR_0]], how are you?"
        # But wait, the server restores the code before returning!
        # So we expect: "[Simulated] Hello %s, how are you?"
        # Let's see if our mock logic preserves the placeholders inside the simulated text.
        # In bridge_server.py:
        #   translated_text = f"[Simulated] {protected_text}"
        #   final_text = processor.restore_control_codes(translated_text, placeholders)
        # If protected_text is "Hello [[VAR_0]]...", translated is "[Simulated] Hello [[VAR_0]]..."
        # restored should be "[Simulated] Hello %s..."

        resp = requests.post(f"{base_url}/translate", json={"text": text_with_code})
        data = resp.json()
        print(f"Response: {data}")
        assert "%s" in data['translated']
        assert "[[VAR" not in data['translated']
        print(">>> PASS")

        # 6. Test Garbage Filtering
        print("\n[Test 5] Garbage Filtering...")
        garbage = "sys_log_001.exe"
        resp = requests.post(f"{base_url}/translate", json={"text": garbage})
        data = resp.json()
        print(f"Response: {data}")
        assert data['status'] == "filtered"
        assert data['translated'] == garbage # Should return original
        print(">>> PASS")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("\n[Test] Terminating Server...")
        server_process.terminate()
        server_process.wait()
        # Clean up test DB
        if os.path.exists("trans_cache.sqlite"):
            os.remove("trans_cache.sqlite")

if __name__ == "__main__":
    run_tests()
