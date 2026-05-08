import redis
import json
import subprocess # <-- NEW: For running OS commands
import shutil     # <-- NEW: For detecting Linux distributions
from pymongo import MongoClient
from datetime import datetime
import time
from ip_identi import classify_ip_add

#Setting up the connection
try:
    r = redis.Redis(host='localhost',port=6379,decode_responses=True)
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['api_monitor']
    inventory = db['inventory']
    print("[+] Connection to Redis and MongoDB established")
except Exception as e:
    print(f"[-] Connection Error: {e}")
    exit()

def get_threshold(api_id):
    # Hot-Reloading: Read the JSON file every time to catch live changes
    try:
        with open('threshold_config.json', 'r') as file:
            config = json.load(file)
            global_default = config.get("global_default", 15)
            custom_limits = config.get("custom_limits", {})
            
            # Return custom limit if it exists, otherwise return the global default
            return custom_limits.get(api_id, global_default)
    except:
        return 15 # Absolute fallback if file is missing/broken
def trigger_os_alert(api_id, suspect_ip, call_count):
    title = f"🚨 Shikra Alert: {api_id}"
    message = f"Mass call spike detected!\nSuspect IP: {suspect_ip}\nCalls: {call_count}"
    
    # Build environment with display session info
    import os
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":0")
    uid = str(os.getuid())
    env.setdefault("DBUS_SESSION_BUS_ADDRESS", f"unix:path=/run/user/{uid}/bus")
    
    try:
        if shutil.which("notify-send"):
            subprocess.Popen(['notify-send', '-u', 'critical', title, message], env=env)
        elif shutil.which("kdialog"):
            subprocess.Popen(['kdialog', '--passivepopup', message, '10', '--title', title], env=env)
        elif shutil.which("zenity"):
            subprocess.Popen(['zenity', '--notification', f'--text={title}\n{message}'], env=env)
        else:
            print(f"\n[CRITICAL] {title} - {message}\n")
    except Exception as e:
        print(f"[-] Failed to send OS notification: {e}")
def sync_data():
    api_call_keys = r.keys("api:*calls")
    
    if not api_call_keys:
        print("[.] No active traffic to sync")
        return

    for key in api_call_keys:
        api_id = key.split(":")[1]
        
        # --- A. CALL COUNT SYNC ---
        new_calls = int(r.getset(key, 0) or 0)
        
        # --- B. TOP CALLER SYNC ---
        top_ip_data = r.zrevrange(f"api:{api_id}:ips",0,0, withscores=True)

        update_fields = {
            "live_state.last_seen": datetime.utcnow(),
            "live_state.health": "working"
        }
        
        top_ip = "Unknown"
        if top_ip_data:
            top_ip, score = top_ip_data[0]
            update_fields["metrics.top_caller.ip"] = top_ip
            update_fields["metrics.top_caller.type"] = classify_ip_add(top_ip)
            r.delete(f"api{api_id}:ips")
        # --- C. DATABASE UPDATE ---
        inventory.update_one(
            {"api_id": api_id},
            {
                "$inc": {"metrics.total_calls": new_calls},
                "$set": update_fields
            }
        )
        print(f"[✔] Synced {api_id}: +{new_calls} calls. Top IP: {top_ip}")

        # --- D. MASS CALL ALERTING ---
        active_threshold = get_threshold(api_id)
        if new_calls > active_threshold:
            print(f"\n[🚨 ALERT] MASS CALL ON {api_id}! ({new_calls} calls, Limit: {active_threshold})")
            
            # --- NEW: Trigger the OS-level notification! ---
            trigger_os_alert(api_id, top_ip, new_calls)
            
            # Log the event permanently in MongoDB
            inventory.update_one(
                {"api_id": api_id},
                {
                    "$push": {
                        "metrics.mass_call_events": {
                            "timestamp": datetime.utcnow(),
                            "spike_count": new_calls,
                            "suspect_ip": top_ip,
                            "threshold_breached": active_threshold
                        }
                    }
                }
            )

if __name__ == "__main__":
    print("[*] Sync Engine Started. Press Ctrl+C to stop.")
    try:
        while True:
            sync_data()
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n[!] Sync Engine stopped.")
