import subprocess
import sys
import time

if __name__ == "__main__":
    # Launch engines silently
    sync_proc = subprocess.Popen([sys.executable, 'data_sync.py'])
    health_proc = subprocess.Popen([sys.executable, 'health_monitor.py'])

    try:
        # Keep the daemon alive so Systemd doesn't think it crashed
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        sync_proc.terminate()
        health_proc.terminate()
