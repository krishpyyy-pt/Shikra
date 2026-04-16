#!/usr/bin/env python3
import os
import sys
import time
import subprocess

# --- PATHING FIX ---
# Forces Shikra to run out of its installation folder, 
# ensuring it can always find your database configs and scripts.
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
os.chdir(BASE_DIR)

active_processes = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """
    ███████╗██╗  ██╗██╗██╗  ██╗██████╗  █████╗ 
    ██╔════╝██║  ██║██║██║ ██╔╝██╔══██╗██╔══██╗
    ███████╗███████║██║█████╔╝ ██████╔╝███████║
    ╚════██║██╔══██║██║██╔═██╗ ██╔══██╗██╔══██║
    ███████║██║  ██║██║██║  ██╗██║  ██║██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
    ===========================================
       Next-Gen API Observability & Gateway
    ===========================================
    """
    print(banner)

def start_engines():
    if active_processes:
        print("\n[-] Shikra Engines are already running!")
        time.sleep(1.5)
        return

    print("\n[*] Booting Shikra Subsystems...")
    try:
        sync_proc = subprocess.Popen(
            [sys.executable, 'data_syn_sc.py'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        health_proc = subprocess.Popen(
            [sys.executable, 'health_monitor.py'], 
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL
        )
        
        active_processes.extend([sync_proc, health_proc])
        print("[✔] Sync Engine: ONLINE")
        print("[✔] Health Watchdog: ONLINE")
        time.sleep(1.5)
    except Exception as e:
        print(f"[-] Failed to start engines: {e}")
        time.sleep(2)

def stop_engines():
    if not active_processes:
        print("\n[.] No engines are currently running.")
        time.sleep(1)
        return

    print("\n[*] Shutting down subsystems...")
    for proc in active_processes:
        proc.terminate()
    active_processes.clear()
    print("[✔] All engines offline.")
    time.sleep(1.5)

def main_menu():
    while True:
        clear_screen()
        print_banner()
        
        status = "🟢 ONLINE" if active_processes else "🔴 OFFLINE"
        print(f"  System Status: {status}\n")
        
        print("  [1] Start Shikra Background Engines")
        print("  [2] Stop Shikra Background Engines")
        print("  [3] Configure Mass Call Thresholds")
        print("  [4] Launch Live API Dashboard") 
        print("  [5] Add New API to Inventory")
        print("  [6] Decommission an API to Inventory")
        print("  [7] Exit\n")
        
        choice = input("shikra > ").strip()
        
        if choice == '1':
            start_engines()
        elif choice == '2':
            stop_engines()
        elif choice == '3':
            clear_screen()
            process = subprocess.run([sys.executable, 'config_manager.py'])
            if process.returncode != 0:
                input("\n[!] CRASH DETECTED: Read the error above and press Enter...")
        elif choice == '4':
            clear_screen()
            process = subprocess.run([sys.executable, 'dashboard.py'])
            if process.returncode != 0:
                input("\n[!] CRASH DETECTED: Read the error above and press Enter...")
        elif choice == '5':
            clear_screen()
            process = subprocess.run([sys.executable, 'inventory_manager.py'])
            if process.returncode != 0:
                input("\n[!] CRASH DETECTED: Read the error above and press Enter...")
        elif choice == '6':
            clear_screen()
            process = subprocess.run([sys.executable, 'decommission_api.py'])
            if process.returncode != 0:
                input("\n[!] CRASH DETECTED: Read the error above and press Enter...")
        elif choice == '7':
            stop_engines()
            print("\nExiting Shikra... Goodbye.")
            sys.exit(0)
        else:
            print("\n[-] Invalid command.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        stop_engines()
        print("\n\n[!] Forced exit. Shikra Engines stopped.")
        sys.exit(0)
