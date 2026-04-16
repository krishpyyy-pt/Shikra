import requests
import redis
from pymongo import MongoClient
from datetime import datetime
import time

# 1. Connections
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['api_monitor']
    inventory = db['inventory']
    print("[+] Watchdog connected to Redis and MongoDB.")
except Exception as e:
    print(f"[-] Connection Error: {e}")
    exit()

def monitor_lifecycle():
    # Only check APIs that haven't been manually "removed"
    apis = inventory.find({"status": {"$ne": "removed"}})

    for api in apis:
        api_id = api['api_id']
        raw_path = api.get('url_path')
        
        if not raw_path:
            print(f"[!] Skipping {api_id}: No url_path found.")
            continue
            
        # --- THE FIX: Prepend the local server address ---
        # Change '5000' if your local API server runs on a different port!
        BASE_URL = "http://127.0.0.1:5000" 
        
        # If it starts with '/', it's a relative path. Add the base URL.
        if raw_path.startswith('/'):
            url = BASE_URL + raw_path
        else:
            url = raw_path # It's already a full URL, leave it alone

        # --- A. CHECK HEALTH (Network) ---
        try:
            # We use a 3-second timeout so one dead API doesn't hang the whole script
            response = requests.get(url, timeout=3)
            health_status = "working" if response.status_code < 500 else "unstable"
        except Exception:
            health_status = "dead"

        # --- B. CHECK ACTIVITY (Redis) ---
        # Look for the status key. If it's expired/missing, it's "at rest"
        live_action = r.get(f"api:{api_id}:status")
        current_activity = live_action if live_action else "at rest"

        # --- C. UPDATE MONGODB ---
        inventory.update_one(
            {"api_id": api_id},
            {
                "$set": {
                    "live_state.health": health_status,
                    "live_state.current_activity": current_activity,
                    "live_state.last_seen": datetime.utcnow()
                }
            }
        )
        print(f"[{api_id}] Health: {health_status} | Activity: {current_activity}")

if __name__ == "__main__":
    print("[*] API Watchdog Started. Press Ctrl+C to stop.")
    try:
        while True:
            monitor_lifecycle()
            print("-" * 40)
            time.sleep(15) # Check every 15 seconds
    except KeyboardInterrupt:
        print("\n[!] Watchdog stopped.")
