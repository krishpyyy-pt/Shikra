import hashlib
import getpass
from pymongo import MongoClient

# Connect to DB
client = MongoClient('mongodb://localhost:27017/')
db = client['api_monitor']
settings = db['system_settings']

print("\n--- 🔐 Shikra Admin Setup ---")
password = getpass.getpass("Create your Master Password: ")
confirm = getpass.getpass("Confirm Master Password: ")

if password == confirm:
    # Hash the password
    pass_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Store it in the database, overwriting any old password
    settings.update_one(
        {"setting": "admin_auth"},
        {"$set": {"hash": pass_hash}},
        upsert=True
    )
    print("\n[✔] Master Password securely hashed and saved to MongoDB.")
else:
    print("\n[-] Passwords do not match. Run setup again.")
