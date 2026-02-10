import os
import csv
import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
NUM_ACCOUNTS = 100
NUM_DEVICES = 50
NUM_TRANSACTIONS = 500

def ensure_output_folder():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"Created directory: {OUTPUT_DIR}")
    else:
        print(f"Directory already exists: {OUTPUT_DIR}")

def generate_data():
    ensure_output_folder()
    
    # 1. Generate Accounts
    print("Generating accounts...")
    accounts = []
    account_ids = []
    account_types = ['personal', 'merchant']
    
    # Create some special "mule" accounts
    mule_accounts = [f"mule_{i}@upi" for i in range(1, 6)]
    
    for i in range(1, NUM_ACCOUNTS + 1):
        if i <= len(mule_accounts):
            account_id = mule_accounts[i-1]
            acc_type = 'personal' # Mules often pretend to be personal
        else:
            account_id = f"user_{i}@upi"
            acc_type = random.choice(account_types)
            
        age = random.randint(10, 1000)
        accounts.append([account_id, age, acc_type])
        account_ids.append(account_id)
        
    with open(os.path.join(OUTPUT_DIR, "accounts.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["account_id", "account_age_days", "account_type"])
        writer.writerows(accounts)

    # 2. Generate Devices and Assignments
    print("Generating devices and associations...")
    device_assignments = [] # List of [device_id, account_id]
    account_device_map = {} # for looking up available devices for a user
    
    # Create normal devices
    devices = [f"dev_{i}" for i in range(1, NUM_DEVICES + 1)]
    
    # Assign devices to accounts
    for acc in account_ids:
        # Standard user: 1 or 2 devices
        # Mule user: might share a device with many others
        
        if "mule" in acc:
            # Mules share a specific set of compromised devices
            assigned_device = devices[0] # All mules use device 0
        else:
            # Normal distribution
            assigned_device = random.choice(devices[1:])
            
        device_assignments.append([assigned_device, acc])
        
        if acc not in account_device_map:
            account_device_map[acc] = []
        account_device_map[acc].append(assigned_device)
        
    with open(os.path.join(OUTPUT_DIR, "devices.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["device_id", "account_id"])
        writer.writerows(device_assignments)

    # 3. Generate Transactions
    print("Generating transactions...")
    transactions = []
    start_date = datetime.now() - timedelta(days=30)
    
    for i in range(1, NUM_TRANSACTIONS + 1):
        txn_id = i
        sender = random.choice(account_ids)
        receiver = random.choice(account_ids)
        while receiver == sender:
            receiver = random.choice(account_ids)
            
        amount = random.randint(100, 50000)
        
        # High value transactions for mules
        if "mule" in sender or "mule" in receiver:
            if random.random() < 0.5:
                amount = random.randint(20000, 100000)
        
        seconds_offset = random.randint(0, 30 * 24 * 60 * 60)
        txn_time = start_date + timedelta(seconds=seconds_offset)
        timestamp_str = txn_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Pick a device for the sender
        sender_devices = account_device_map.get(sender, [])
        if sender_devices:
            device_id = random.choice(sender_devices)
        else:
            device_id = "dev_unknown"
            
        transactions.append([txn_id, sender, receiver, amount, timestamp_str, device_id])
        
    with open(os.path.join(OUTPUT_DIR, "transactions.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["txn_id", "sender", "receiver", "amount", "timestamp", "device_id"])
        writer.writerows(transactions)

    print("Data generation complete.")

if __name__ == "__main__":
    generate_data()
