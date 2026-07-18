import time
import requests

def run_test():
    success_count = 0
    fail_count = 0
    total = 25  # 25 requests so we can see the browser reset after 20 solves
    
    print("Starting stress test (1 request every 5s)...")
    for i in range(1, total + 1):
        print(f"\n--- Request {i}/{total} ---")
        start = time.time()
        try:
            resp = requests.get("http://127.0.0.1:8080/getToken", timeout=90)
            if resp.status_code == 200:
                data = resp.json()
                print(f"[SUCCESS] Token obtained in {data.get('elapsed_s')}s (Attempts: {data.get('attempts')})")
                success_count += 1
            else:
                print(f"[FAILED] HTTP {resp.status_code} - {resp.text}")
                fail_count += 1
        except Exception as e:
            print(f"[ERROR] Could not connect to solver: {e}")
            print("MAKE SURE YOUR SOLVER IS RUNNING (start-solver.bat)")
            fail_count += 1
            
        elapsed = time.time() - start
        sleep_time = max(0, 5 - elapsed)
        if i < total:
            print(f"Waiting {sleep_time:.1f}s before next request...")
            time.sleep(sleep_time)
            
    print("\n=== Test Complete ===")
    print(f"Total: {total}, Success: {success_count}, Failures: {fail_count}")

if __name__ == "__main__":
    run_test()
