import threading
import time
import requests
import sys
import os
import subprocess

def run_tests():
    print("=== Starting Overlay Integration Tests (Async) ===")

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

    try:
        # 2. Test Initial State
        print("\n[Test 1] Checking Empty State...")
        resp = requests.get(f"{base_url}/latest")
        data = resp.json()
        assert "Waiting for text" in data['translated']
        print(">>> PASS")

        # 3. Push Translation
        print("\n[Test 2] Pushing Text to Server...")
        requests.post(f"{base_url}/translate", json={"text": "Hello World"})

        # 4. Verify Latest Endpoint Update (Wait for Async)
        print("\n[Test 3] Verifying /latest Update...")

        found = False
        for _ in range(10): # Wait up to 2 seconds
            resp = requests.get(f"{base_url}/latest")
            data = resp.json()
            if "Hello World" in data.get('original', ''):
                found = True
                print(f"Overlay Data: {data}")
                assert "Simulated" in data['translated']
                break
            time.sleep(0.2)

        if not found:
            raise Exception("Timeout waiting for Overlay update")

        print(">>> PASS")

        print("\n[Test] Overlay Integration Logic Verified (Headless).")

    except Exception as e:
        print(f"FAIL: {e}")
    finally:
        print("\n[Test] Terminating Server...")
        server_process.terminate()
        server_process.wait()
        if os.path.exists("trans_cache.sqlite"):
            os.remove("trans_cache.sqlite")

if __name__ == "__main__":
    run_tests()
