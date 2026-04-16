import sys
import os
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

def add_new_api():
    clear_screen()
    print("\n  ████████████████████████████████████████████████████")
    print("                 SHIKRA INVENTORY MANAGER             ")
    print("  ████████████████████████████████████████████████████\n")

    # 1. Essential Routing Info
    api_id = input("  [?] Enter unique API ID (e.g., Payment_Gateway_v2): ").strip()

    if not api_id:
        print("\n  [-] Error: API ID cannot be empty.")
        input("\n  Press Enter to return...")
        return

    # Duplicate check to protect database integrity
    if inventory.find_one({"api_id": api_id}):
        print(f"\n  [-] Error: API ID '{api_id}' already exists in the database.")
        input("\n  Press Enter to return...")
        return

    name = input("  [?] Enter Human-Readable Name: ").strip()
    url_path = input("  [?] Enter URL Path (e.g., /api/v2/pay): ").strip()
    
    # 2. Categorization
    category = input("  [?] Enter Category (e.g., Finance, Auth, Download): ").strip()
    if not category: category = "General"

    print("\n  --- Risk Levels: [1] Low  [2] Moderate  [3] High  [4] Critical ---")
    risk_choice = input("  [?] Select Risk Level (1-4): ").strip()
    risk_map = {'1': 'Low', '2': 'Moderate', '3': 'High', '4': 'Critical'}
    risk_level = risk_map.get(risk_choice, 'Moderate') # Defaults to Moderate

    # 3. Technical Details
    methods_raw = input("\n  [?] Expected HTTP Methods (comma-separated, e.g., GET, POST): ").strip().upper()
    expected_methods = [m.strip() for m in methods_raw.split(',')] if methods_raw else ["GET"]

    extra_notes = input("  [?] Enter Extra Notes (Optional): ").strip()

    # 4. Constructing the clean document
    new_api_doc = {
        "api_id": api_id,
        "name": name if name else api_id,
        "url_path": url_path,
        "category": category,
        "status": "active",
        "risk_level": risk_level,
        "expected_methods": expected_methods,
        "extra_notes": extra_notes,
        "first_added": datetime.utcnow(),
        # Initialize the live states so the Dashboard doesn't break
        "live_state": {
            "current_activity": "at rest",
            "last_seen": None,
            "health": "unknown"
        },
        "metrics": {
            "total_calls": 0,
            "top_caller": {},
            "mass_call_events": []
        },
        "removed_at": None
    }

    # 5. Database Insertion
    try:
        inventory.insert_one(new_api_doc)
        print(f"\n  [✔] Successfully added '{api_id}' to Shikra Inventory.")
    except Exception as e:
        print(f"\n  [-] Failed to add API: {e}")

    input("\n  Press Enter to return to Shikra Console...")

if __name__ == "__main__":
    add_new_api()
