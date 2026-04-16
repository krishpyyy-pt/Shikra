import sys
import os
import getpass
import hashlib
from datetime import datetime
from pymongo import MongoClient

# --- Database Connection ---
try:
    mongo_client = MongoClient('mongodb://localhost:27017/')
    db = mongo_client['api_monitor']
    inventory = db['inventory']
except Exception as e:
    print(f"[-] Database Error: {e}")
    sys.exit(1)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def decommission_api():
    clear_screen()
    print("\n  ████████████████████████████████████████████████████")
    print("                SHIKRA DECOMMISSION MODULE            ")
    print("  ████████████████████████████████████████████████████\n")

    # Show all APIs (including already decommissioned ones if they want to hard purge them)
    all_apis = list(inventory.find({}, {"api_id": 1, "name": 1, "status": 1}))
    
    if not all_apis:
        print("  [.] No APIs found in the inventory.")
        input("\n  Press Enter to return...")
        return

    print("  --- API Inventory ---")
    for api in all_apis:
        status_tag = "[Archived]" if api.get("status") == "removed" else "[Active]"
        print(f"    - {api['api_id']} {status_tag}")

    print("\n  " + "-" * 50)
    target_id = input("  [?] Enter the API ID to target (or type 'cancel'): ").strip()

    if target_id.lower() == 'cancel' or not target_id:
        return

    target_api = inventory.find_one({"api_id": target_id})

    if not target_api:
        print(f"\n  [-] Error: '{target_id}' not found in database.")
        input("\n  Press Enter to return...")
        return

    # Choose the deletion method
    print("\n  --- Select Deletion Method ---")
    print("  [1] Soft Decommission (Archive traffic data, hide from live dashboard)")
    print("  [2] Hard Purge (PERMANENTLY delete all records and history)")
    
    del_choice = input("\n  Select option: ").strip()

    if del_choice == '1':
        if target_api.get("status") == "removed":
            print(f"\n  [.] '{target_id}' is already decommissioned.")
        else:
            inventory.update_one(
                {"api_id": target_id},
                {"$set": {"status": "removed", "removed_at": datetime.utcnow()}}
            )
            print(f"\n  [✔] '{target_id}' has been safely decommissioned and archived.")

    elif del_choice == '2':
        print(f"\n  [!!!] NUCLEAR WARNING: You are about to permanently eradicate '{target_id}'.")
        
        # --- 1. Fetch the True Hash from MongoDB ---
        # Look inside the system_settings collection for the master hash
        auth_record = db['system_settings'].find_one({"setting": "admin_auth"})
        
        if not auth_record or "hash" not in auth_record:
            print("\n  [-] CRITICAL ERROR: Master Password not configured in database.")
            print("      Run the setup script to initialize system security.")
            input("\n  Press Enter to return...")
            return
            
        EXPECTED_HASH = auth_record["hash"]
        
        # --- 2. The Access Control Check ---
        print("  [!] Elevated privileges required for this action.")
        attempt = getpass.getpass("      Enter Master Password: ") 
        
        # Hash their attempt to see if it matches the master hash
        attempt_hash = hashlib.sha256(attempt.encode()).hexdigest()
        
        if attempt_hash != EXPECTED_HASH:
            print("\n  [-] Authentication Failed. Incident logged. Purge aborted.")
            input("\n  Press Enter to return...")
            return

        # --- 3. The Accidental Typo Check ---
        confirm = input(f"\n  [?] Auth Success. Type '{target_id}' exactly to confirm purge: ").strip()
        
        if confirm == target_id:
            # The actual Hard Delete command
            inventory.delete_one({"api_id": target_id})
            print(f"\n  [✔] '{target_id}' has been completely purged from the database.")
        else:
            print("\n  [-] Confirmation mismatch. Purge aborted.")
            
    else:
        print("\n  [-] Invalid choice. Aborting.")

    input("\n  Press Enter to return to Shikra Console...")

if __name__ == "__main__":
    decommission_api()
