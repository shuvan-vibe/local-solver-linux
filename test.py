import requests
import time

for i in range(1, 4):
    print(f"\n--- Request {i} ---")
    start = time.time()
    try:
        response = requests.get("http://127.0.0.1:8080/getToken", timeout=60)
        print(f"Status: {response.status_code}")
        print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print(f"Time taken: {time.time() - start:.2f}s")
    time.sleep(2)
