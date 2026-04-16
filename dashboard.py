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

def format_date(date_obj):
    """Safely formats MongoDB datetime objects to strings."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime('%Y-%m-%d %H:%M:%S')
    return str(date_obj) if date_obj else "N/A"

def print_cards(apis):
    """Draws a highly detailed, two-column ASCII card for each API."""
    if not apis:
        print("\n  [-] No APIs found matching this criteria.\n")
        return

    for api in apis:
        # --- 1. Data Extraction & Formatting ---
        api_id = str(api.get("api_id", "Unknown"))
        name = str(api.get("name", "Unnamed API"))
        path = str(api.get("url_path", "N/A"))[:26] # Truncate if too long to save the box
        category = str(api.get("category", "General"))
        status = str(api.get("status", "Unknown"))
        risk = str(api.get("risk_level", "Unknown"))
        
        methods_list = api.get("expected_methods", [])
        methods = ", ".join(methods_list) if methods_list else "None"
        
        added = format_date(api.get("first_added"))
        removed = api.get("removed_at")

        # Nested: Live State
        live_state = api.get("live_state", {})
        health = str(live_state.get("health", "unknown"))
        activity = str(live_state.get("current_activity", "unknown"))[:26]
        seen = format_date(live_state.get("last_seen"))

        # Nested: Metrics
        metrics = api.get("metrics", {})
        calls = str(metrics.get("total_calls", 0))
        mass_events = len(metrics.get("mass_call_events", []))
        
        top_caller = metrics.get("top_caller", {})
        top_ip = str(top_caller.get("ip", "None"))
        top_type = str(top_caller.get("type", "None"))[:26]

        notes = str(api.get("extra_notes", "None"))[:80]

        # Health Icon Logic
        if health == "working":
            h_icon, h_text = "🟢", "Working"
        elif health == "dead":
            h_icon, h_text = "🔴", "Dead"
        else:
            h_icon, h_text = "🟡", health.capitalize()

        # --- 2. Drawing the ASCII Card ---
        print(f"\n  ╔════════════════════════════════════════════════════════════════════════════════════╗")
        print(f"  ║ {h_icon} [{api_id}] {name:<65} ║")
        print(f"  ╠════════════════════════════════════════╦═══════════════════════════════════════════╣")
        print(f"  ║ 🌐 ROUTING & META                      ║ 📊 METRICS & HEALTH                       ║")
        print(f"  ║ Path     : {path:<27} ║ Health   : {h_text:<32} ║")
        print(f"  ║ Category : {category:<27} ║ Activity : {activity:<32} ║")
        print(f"  ║ Methods  : {methods:<27} ║ Calls    : {calls:<32} ║")
        print(f"  ║ Status   : {status:<27} ║ Top IP   : {top_ip:<32} ║")
        print(f"  ║ Risk     : {risk:<27} ║ IP Type  : {top_type:<32} ║")
        print(f"  ║ Added    : {added:<27} ║ Seen     : {seen:<32} ║")
        
        # Only draw the removed_at line if it actually has data
        if removed:
            print(f"  ║ Removed  : {format_date(removed):<27} ║                                           ║")
            
        print(f"  ╠════════════════════════════════════════╩═══════════════════════════════════════════╣")
        print(f"  ║ 📝 Notes  : {notes:<71} ║")
        
        # Dynamic alerting for Mass Calls
        if mass_events > 0:
            print(f"  ║ 🚨 Alerts : {mass_events} mass call events recorded! Check DB for forensics.               ║")
        else:
            print(f"  ║ 🛡️  Alerts : 0 mass call events. System stable.                                    ║")
            
        print(f"  ╚════════════════════════════════════════════════════════════════════════════════════╝")


def view_all():
    apis = list(inventory.find({"status": {"$ne": "removed"}}))
    print_cards(apis)

def view_by_category():
    categories = inventory.distinct("category", {"status": {"$ne": "removed"}})
    
    if not categories or categories == [None]:
        print("\n  [-] No categories found in the database.")
        return

    print("\n  --- Available Categories ---")
    for i, cat in enumerate(categories, 1):
        print(f"    [{i}] {cat}")
        
    try:
        choice = int(input("\n  Select a category number: ").strip())
        selected_cat = categories[choice - 1]
        
        apis = list(inventory.find({"category": selected_cat, "status": {"$ne": "removed"}}))
        clear_screen()
        print(f"\n  [*] Filtering Dashboard by Category: {selected_cat}")
        print_cards(apis)
    except (ValueError, IndexError):
        print("  [-] Invalid selection.")

def dashboard_menu():
    while True:
        clear_screen()
        print("\n  ████████████████████████████████████████████████████████████████████████████")
        print("                            SHIKRA OBSERVATORY                                ")
        print("  ████████████████████████████████████████████████████████████████████████████\n")
        print("    [1] View All Active APIs")
        print("    [2] Filter APIs by Category")
        print("    [3] Return to Shikra Console\n")
        
        choice = input("  dashboard > ").strip()
        
        if choice == '1':
            clear_screen()
            view_all()
            input("\n  Press Enter to return...")
        elif choice == '2':
            clear_screen()
            view_by_category()
            input("\n  Press Enter to return...")
        elif choice == '3':
            break
        else:
            print("  [-] Invalid command.")

if __name__ == "__main__":
    dashboard_menu()
