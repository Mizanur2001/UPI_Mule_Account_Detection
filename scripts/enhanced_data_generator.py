"""
Enhanced synthetic data generator with realistic mule account scenarios.
Creates test cases for Stage III MVP demonstration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set seed for reproducibility
np.random.seed(42)
random.seed(42)

# ============================================================================
# SCENARIO 1: STAR AGGREGATOR MULE (5 friends → 1 collector → distributor)
# ============================================================================
def create_star_aggregator_scenario(base_idx=0):
    """Classic mule: many sources converge to one account, then distributes."""
    transactions = []
    devices = []
    accounts = []
    
    # Create 5 "customer" accounts (legitimate users)
    customers = [f"customer_{i}@upi" for i in range(1, 6)]
    for cust in customers:
        accounts.append({
            "account_id": cust,
            "account_age_days": np.random.randint(100, 500)
        })
        devices.append({"account_id": cust, "device_id": f"device_{random.randint(1000, 9999)}"})
    
    # Create MULE account (new, high activity)
    mule_aggregator = f"mule_aggregator@upi"
    accounts.append({"account_id": mule_aggregator, "account_age_days": 5})  # Very new!
    
    # All 5 customers send to mule
    for cust in customers:
        for _ in range(2):  # Each customer sends 2x
            transactions.append({
                "sender": cust,
                "receiver": mule_aggregator,
                "amount": np.random.randint(2000, 8000)
            })
    
    # Mule sends to distributor with high pass-through
    total_received = sum([t["amount"] for t in transactions if t["receiver"] == mule_aggregator])
    
    distributor = f"distributor_{random.randint(1000, 9999)}@upi"
    transactions.append({
        "sender": mule_aggregator,
        "receiver": distributor,
        "amount": int(total_received * 0.95)  # 95% pass-through
    })
    
    # Wire to multiple sinks from distributor
    sinks = [f"sink_{i}@upi" for i in range(1, 4)]
    for sink in sinks:
        transactions.append({
            "sender": distributor,
            "receiver": sink,
            "amount": np.random.randint(5000, 15000)
        })
        accounts.append({"account_id": sink, "account_age_days": np.random.randint(200, 800)})
        devices.append({"account_id": sink, "device_id": f"device_{random.randint(1000, 9999)}"})
    
    # Device link: Same device on mule + distributor (proof of coordination)
    device_id = f"device_mule_001"
    devices.append({"account_id": mule_aggregator, "device_id": device_id})
    devices.append({"account_id": distributor, "device_id": device_id})
    
    return transactions, accounts, devices


# ============================================================================
# SCENARIO 2: CIRCULAR MULE NETWORK (A→B→C→A loop for fund rotation)
# ============================================================================
def create_circular_network_scenario():
    """Circular laundering: funds rotate through network to obscure origin."""
    transactions = []
    devices = []
    accounts = []
    
    # 4 accounts in a circle
    circle = [f"circle_node_{i}@upi" for i in range(1, 5)]
    
    for node in circle:
        accounts.append({"account_id": node, "account_age_days": np.random.randint(30, 200)})
        # All use same device (highly suspicious)
        devices.append({"account_id": node, "device_id": "device_circle_cartel"})
    
    # Create circular flow: A→B→C→D→A
    amount = 15000
    for i in range(len(circle)):
        sender = circle[i]
        receiver = circle[(i + 1) % len(circle)]
        
        # Multiple rotations
        for _ in range(3):
            transactions.append({
                "sender": sender,
                "receiver": receiver,
                "amount": amount + np.random.randint(-500, 500)
            })
    
    return transactions, accounts, devices


# ============================================================================
# SCENARIO 3: CHAIN LAUNDERING (A→B→C→D→E linear path)
# ============================================================================
def create_chain_laundering_scenario():
    """Money laundering chain: progresses through multiple intermediaries."""
    transactions = []
    devices = []
    accounts = []
    
    chain = [f"chain_node_{i}@upi" for i in range(1, 6)]
    
    for node in chain:
        accounts.append({"account_id": node, "account_age_days": np.random.randint(50, 300)})
        devices.append({"account_id": node, "device_id": f"device_{hash(node) % 10000}"})
    
    # Linear chain with amount decay (to avoid exact matches)
    amount = 25000
    for i in range(len(chain) - 1):
        for _ in range(2):  # Each link processes 2 transactions
            transactions.append({
                "sender": chain[i],
                "receiver": chain[i + 1],
                "amount": int(amount * (1 - 0.05 * (i + 1)))  # Slight decrease
            })
    
    return transactions, accounts, devices


# ============================================================================
# SCENARIO 4: DEVICE-BASED MULE RING (Same device, multiple accounts)
# ============================================================================
def create_device_ring_scenario():
    """Multiple accounts controlled by same device."""
    transactions = []
    devices = []
    accounts = []
    
    # 3 accounts all using same device
    mule_ring = [f"device_ring_{i}@upi" for i in range(1, 4)]
    shared_device = "device_fraud_ring_001"
    
    for i, acc in enumerate(mule_ring):
        accounts.append({"account_id": acc, "account_age_days": np.random.randint(10, 40)})
        devices.append({"account_id": acc, "device_id": shared_device})
    
    # Inter-account transfers (moving money between ring accounts)
    for i, acc in enumerate(mule_ring):
        receiver = mule_ring[(i + 1) % len(mule_ring)]
        transactions.append({
            "sender": acc,
            "receiver": receiver,
            "amount": np.random.randint(8000, 20000)
        })
    
    return transactions, accounts, devices


# ============================================================================
# SCENARIO 5: NEW ACCOUNT RAPID ONBOARDING FRAUD
# ============================================================================
def create_rapid_onboarding_scenario():
    """High-risk pattern: brand new account with immediate high velocity."""
    transactions = []
    devices = []
    accounts = []
    
    # New account (1 day old!)
    new_mule = "new_mule_account@upi"
    accounts.append({"account_id": new_mule, "account_age_days": 1})
    devices.append({"account_id": new_mule, "device_id": "device_burner_001"})
    
    # Immediate rapid activity
    for _ in range(8):
        transactions.append({
            "sender": f"source_{random.randint(1000, 9999)}@upi",
            "receiver": new_mule,
            "amount": np.random.randint(3000, 12000)
        })
    
    # Immediate send-out
    total_in = sum([t["amount"] for t in transactions if t["receiver"] == new_mule])
    for _ in range(5):
        transactions.append({
            "sender": new_mule,
            "receiver": f"sink_{random.randint(1000, 9999)}@upi",
            "amount": int(total_in * 0.18)
        })
    
    return transactions, accounts, devices


# ============================================================================
# LEGITIMATE BACKGROUND TRAFFIC
# ============================================================================
def create_legitimate_background_traffic(num_accounts=15):
    """Normal UPI traffic for baseline."""
    transactions = []
    devices = []
    accounts = []
    
    for i in range(num_accounts):
        acc = f"legitimate_{i}@upi"
        accounts.append({"account_id": acc, "account_age_days": np.random.randint(100, 900)})
        devices.append({"account_id": acc, "device_id": f"device_{i}"})
    
    # Normal transaction patterns
    for _ in range(30):
        sender = f"legitimate_{random.randint(0, num_accounts-1)}@upi"
        receiver = f"legitimate_{random.randint(0, num_accounts-1)}@upi"
        if sender != receiver:
            transactions.append({
                "sender": sender,
                "receiver": receiver,
                "amount": np.random.randint(500, 5000)
            })
    
    return transactions, accounts, devices


# ============================================================================
# MAIN GENERATOR
# ============================================================================
def generate_enhanced_dataset():
    """Generate complete test dataset with realistic mule scenarios."""
    
    all_txns = []
    all_accounts = []
    all_devices = []
    
    print("Generating mule scenarios...")
    
    # Scenario 1: Star Aggregator
    txns, accs, devs = create_star_aggregator_scenario()
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Star aggregator scenario created")
    
    # Scenario 2: Circular Network
    txns, accs, devs = create_circular_network_scenario()
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Circular network scenario created")
    
    # Scenario 3: Chain Laundering
    txns, accs, devs = create_chain_laundering_scenario()
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Chain laundering scenario created")
    
    # Scenario 4: Device Ring
    txns, accs, devs = create_device_ring_scenario()
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Device ring scenario created")
    
    # Scenario 5: Rapid Onboarding
    txns, accs, devs = create_rapid_onboarding_scenario()
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Rapid onboarding scenario created")
    
    # Legitimate traffic baseline
    txns, accs, devs = create_legitimate_background_traffic(25)
    all_txns.extend(txns)
    all_accounts.extend(accs)
    all_devices.extend(devs)
    print("✅ Legitimate background traffic created")
    
    # Convert to DataFrames
    txns_df = pd.DataFrame(all_txns)
    accounts_df = pd.DataFrame(all_accounts)
    devices_df = pd.DataFrame(all_devices)
    
    # Remove duplicates and clean
    accounts_df = accounts_df.drop_duplicates(subset=["account_id"], keep="first").reset_index(drop=True)
    devices_df = devices_df.drop_duplicates(subset=["account_id", "device_id"], keep="first").reset_index(drop=True)
    txns_df = txns_df.dropna().reset_index(drop=True)
    
    return txns_df, accounts_df, devices_df


# ============================================================================
# SAVE DATASETS
# ============================================================================
if __name__ == "__main__":
    print("🚀 Generating enhanced test dataset with mule scenarios...\n")
    
    txns, accounts, devices = generate_enhanced_dataset()
    
    # Save
    txns.to_csv("data/transactions.csv", index=False)
    accounts.to_csv("data/accounts.csv", index=False)
    devices.to_csv("data/devices.csv", index=False)
    
    print(f"\n📊 Dataset Summary:")
    print(f"  • Transactions: {len(txns)}")
    print(f"  • Unique Accounts: {len(accounts)}")
    print(f"  • Device Mappings: {len(devices)}")
    print(f"\n✅ Saved to data/ directory")
    print(f"\n🎯 Known Mule Accounts to Look For:")
    print(f"  • Star Aggregator: mule_aggregator@upi (score: HIGH)")
    print(f"  • Circular Network: circle_node_*@upi (score: HIGH)")
    print(f"  • Chain Laundering: chain_node_*@upi (score: HIGH)")
    print(f"  • Device Ring: device_ring_*@upi (score: HIGH)")
    print(f"  • Rapid Onboarding: new_mule_account@upi (score: HIGH)")
