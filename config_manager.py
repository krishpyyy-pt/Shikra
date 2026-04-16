import json
import os
import sys
from pymongo import MongoClient

CONFIG_FILE = 'threshold_config.json'

# --- MongoDB Connection ---
try:
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['api_monitor']
    inventory = db['inventory']
except Exception as e:
    print(f"[-] Database Error: {e}")
    sys.exit(1)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        # Create a default file if it doesn't exist
        default_config = {"global_default": 15, "custom_limits": {}}
        save_config(default_config)
        return default_config
    
    with open(CONFIG_FILE, 'r') as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            print("[-] Error reading config file. Reverting to defaults.")
            return {"global_default": 15, "custom_limits": {}}

def save_config(config_data):
    with open(CONFIG_FILE, 'w') as file:
        json.dump(config_data, file, indent=4)

def manage_config():
    config = load_config()
    
    while True:
        print("\n--- ⚙️ Threshold Configuration ---")
        print(f"1. Change Global Default (Current: {config['global_default']})")
        print("2. Set Custom Limit for Specific API")
        print("3. View All Custom Limits")
        print("4. Return to Main Menu")
        
        choice = input("Select option: ").strip()
        
        if choice == '1':
            try:
                new_limit = int(input("Enter new Global Default: "))
                config['global_default'] = new_limit
                save_config(config)
                print(f"[✔] Global Default updated to {new_limit}")
            except ValueError:
                print("[-] Please enter a valid number.")
                
        elif choice == '2':
            api_id = input("Enter API ID (e.g., Login_API): ").strip()
            
            # --- THE NEW VERIFICATION CHECK ---
            # Ask MongoDB if this API actually exists before proceeding
            if not inventory.find_one({"api_id": api_id}):
                print(f"[-] Error: API '{api_id}' does not exist in the database.")
                print("    Please check the ID and try again.")
                continue # Skips the rest of the loop and asks for input again
                
            try:
                limit = int(input(f"Enter custom threshold for {api_id}: "))
                config['custom_limits'][api_id] = limit
                save_config(config)
                print(f"[✔] Custom limit for {api_id} set to {limit}")
            except ValueError:
                print("[-] Please enter a valid number.")
                
        elif choice == '3':
            print("\n--- Current Custom Limits ---")
            if not config['custom_limits']:
                print("No custom limits set.")
            else:
                for api, limit in config['custom_limits'].items():
                    print(f" - {api}: {limit} calls/30s")
                    
        elif choice == '4':
            break
        else:
            print("[-] Invalid choice.")

if __name__ == "__main__":
    manage_config()
