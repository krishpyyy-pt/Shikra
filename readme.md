# 🦅 Shikra: Next-Gen API Observability & Security Gateway

Shikra is a lightweight, high-performance API observability engine and firewall designed for Linux environments. It operates by capturing traffic via Redis and executing continuous health and security audits asynchronously, triggering native OS-level alerts when mass-call attacks or DDoS attempts are detected.

Featuring a fully interactive Terminal User Interface (TUI), Shikra allows security analysts to manage API lifecycles, configure real-time thresholds, and perform incident forensics without ever leaving the command line.

---

## ⚙️ Core Architecture

Shikra is built to monitor network traffic without creating bottlenecks on your primary web server (e.g., Nginx). 

* **High-Speed Ingestion:** Utilizes Redis to capture API call counts and IP metrics asynchronously.
* **The Watchdog Engine:** A background synchronization engine that analyzes traffic against dynamic, hot-reloadable JSON thresholds.
* **Persistent Forensics:** Logs all threshold breaches and attacker IP profiles to MongoDB for deep-dive security audits.
* **Native OS Alerts:** Distro-agnostic Linux notifications (`notify-send`, `kdialog`, `zenity`) trigger instantly upon attack detection.
* **Secure Lifecycle Management:** Requires SHA-256 hashed Master Password authentication for hard-purging database records.

---

## 📋 Prerequisites

Before installing Shikra, ensure your system has the following running:
* **OS:** Linux (Debian/Ubuntu recommended)
* **Python:** 3.8+
* **Databases:** Redis Server & MongoDB (running on default localhost ports)

```bash
# Example for Debian/Ubuntu:
sudo apt update
sudo apt install redis-server mongodb python3 python3-pip
🚀 Installation & Setup
1. Clone the Repository

Bash
git clone [https://github.com/yourusername/shikra.git](https://github.com/yourusername/shikra.git)
cd shikra
2. Install Python Dependencies

Bash
pip install -r requirements.txt
3. Configure the Master Security Password
Shikra requires a Master Password to authorize destructive actions (like hard-purging an API from the database). Run the one-time setup script to generate a secure SHA-256 hash in your database:

Bash
python3 setup_auth.py
4. Install Globally
Run the included installer script to create a global symlink. This allows you to launch Shikra from anywhere on your system.

Bash
chmod +x install.sh
./install.sh
💻 Usage: The Master Console
Once installed, simply type shikra into any terminal to launch the interactive Master Console.

Plaintext
    ███████╗██╗  ██╗██╗██╗  ██╗██████╗  █████╗ 
    ██╔════╝██║  ██║██║██║ ██╔╝██╔══██╗██╔══██╗
    ███████╗███████║██║█████╔╝ ██████╔╝███████║
    ╚════██║██╔══██║██║██╔═██╗ ██╔══██╗██╔══██║
    ███████║██║  ██║██║██║  ██╗██║  ██║██║  ██║
    ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
Main Menu Options:
[1] Start Background Engines: Boots the Redis-to-Mongo sync and health monitoring Watchdog.

[2] Stop Background Engines: Safely terminates the background monitoring processes.

[3] Configure Mass Call Thresholds: Set global or API-specific rate limits. Changes hot-reload instantly.

[4] Launch Live API Dashboard: View a real-time, color-coded ASCII matrix of your entire API inventory, health status, and live traffic.

[5] Add New API to Inventory: Interactive wizard to onboard a new endpoint.

[6] View Forensics & Incident Logs: View detailed chronologies of mass-call attacks, including exact timestamps and suspect IPs.

[7] Decommission an API: Soft-delete (archive) or Hard-Purge (requires Master Password) an API from the system.

🛡️ Running Shikra as a Background Daemon (Optional)
For production environments, you can configure Shikra's Watchdog engines to boot automatically with your operating system using systemd.

Edit the service file path to match your installation directory:

Bash
sudo nano /etc/systemd/system/shikra.service
Enable and start the daemon:

Bash
sudo systemctl enable shikra
sudo systemctl start shikra
Note: Even when running as a daemon, you can still launch the shikra console at any time to view the dashboard and manage settings.

👨‍💻 Author
Kavyansh * Aspiring Cyber Security Analyst

Portfolio: kavyansh_.me
