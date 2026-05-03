import redis
import time

try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
except Exception as e:
    print("[-] Redis not running.")
    exit()

TARGET_API = "testAt"
ROGUE_IP = "192.168.1.99"
ATTACK_VOLUME = 45 # This will easily breach the default threshold of 15

print(f"[*] Launching simulated DDoS on {TARGET_API} from {ROGUE_IP}...")

for i in range(ATTACK_VOLUME):
    # 1. Increment the call counter
    r.incr(f"api:{TARGET_API}:calls")
    
    # 2. Add the IP to the sorted set to simulate the "Top Caller"
    r.zadd(f"api:{TARGET_API}:ips", {ROGUE_IP: 1}, incr=True)
    
    if i % 10 == 0:
        print(f"  -> Injected {i} malicious requests...")
    time.sleep(0.05) # Super fast injection

print(f"[✔] Attack complete. {ATTACK_VOLUME} payloads delivered.")
