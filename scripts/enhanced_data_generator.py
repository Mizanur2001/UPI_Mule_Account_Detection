"""
Enhanced synthetic data generator with realistic mule account scenarios.
Includes timestamps, device fingerprints, and multiple fraud typologies
for Stage III prototype demonstration.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Reproducibility
np.random.seed(42)
random.seed(42)

BASE_TIME = datetime(2026, 2, 10, 8, 0, 0)  # Start date for scenarios


def _rand_ts(base, hours_range=(0, 48), minute_jitter=30):
    """Generate a random timestamp near `base`."""
    offset = timedelta(
        hours=np.random.randint(*hours_range),
        minutes=np.random.randint(0, minute_jitter),
        seconds=np.random.randint(0, 60),
    )
    return (base + offset).isoformat()


# ============================================================================
# SCENARIO 1: STAR AGGREGATOR MULE (5 sources → 1 collector → distributor)
# ============================================================================
def create_star_aggregator_scenario():
    transactions, devices, accounts = [], [], []

    customers = [f"customer_{i}@upi" for i in range(1, 6)]
    for cust in customers:
        accounts.append({"account_id": cust, "account_age_days": np.random.randint(100, 500)})
        devices.append({"account_id": cust, "device_id": f"device_{random.randint(1000, 9999)}"})

    mule = "mule_aggregator@upi"
    accounts.append({"account_id": mule, "account_age_days": 5})

    # 5 customers send to mule — burst pattern
    base = BASE_TIME
    for cust in customers:
        for j in range(2):
            transactions.append({
                "sender": cust, "receiver": mule,
                "amount": np.random.randint(2000, 8000),
                "timestamp": _rand_ts(base, (0, 4), 15),  # All within ~4 hours
            })

    total_received = sum(t["amount"] for t in transactions if t["receiver"] == mule)

    distributor = "distributor_main@upi"
    accounts.append({"account_id": distributor, "account_age_days": 45})
    transactions.append({
        "sender": mule, "receiver": distributor,
        "amount": int(total_received * 0.95),
        "timestamp": _rand_ts(base, (5, 8)),
    })

    sinks = [f"sink_{i}@upi" for i in range(1, 4)]
    for sink in sinks:
        transactions.append({
            "sender": distributor, "receiver": sink,
            "amount": np.random.randint(5000, 15000),
            "timestamp": _rand_ts(base, (9, 14)),
        })
        accounts.append({"account_id": sink, "account_age_days": np.random.randint(200, 800)})
        devices.append({"account_id": sink, "device_id": f"device_{random.randint(1000, 9999)}"})

    # Same device on mule + distributor
    devices.append({"account_id": mule, "device_id": "device_mule_001"})
    devices.append({"account_id": distributor, "device_id": "device_mule_001"})

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 2: CIRCULAR MULE NETWORK (A→B→C→D→A loop)
# ============================================================================
def create_circular_network_scenario():
    transactions, devices, accounts = [], [], []

    circle = [f"circle_node_{i}@upi" for i in range(1, 5)]
    for node in circle:
        accounts.append({"account_id": node, "account_age_days": np.random.randint(30, 200)})
        devices.append({"account_id": node, "device_id": "device_circle_cartel"})

    amount = 15000
    base = BASE_TIME + timedelta(hours=2)
    for i in range(len(circle)):
        sender = circle[i]
        receiver = circle[(i + 1) % len(circle)]
        for r in range(3):
            transactions.append({
                "sender": sender, "receiver": receiver,
                "amount": amount + np.random.randint(-500, 500),
                "timestamp": _rand_ts(base, (r * 4, r * 4 + 3)),
            })

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 3: CHAIN LAUNDERING  (A→B→C→D→E)
# ============================================================================
def create_chain_laundering_scenario():
    transactions, devices, accounts = [], [], []

    chain = [f"chain_node_{i}@upi" for i in range(1, 6)]
    for node in chain:
        accounts.append({"account_id": node, "account_age_days": np.random.randint(50, 300)})
        devices.append({"account_id": node, "device_id": f"device_{hash(node) % 10000}"})

    amount = 25000
    base = BASE_TIME + timedelta(hours=6)
    for i in range(len(chain) - 1):
        for t in range(2):
            transactions.append({
                "sender": chain[i], "receiver": chain[i + 1],
                "amount": int(amount * (1 - 0.05 * (i + 1))),
                "timestamp": _rand_ts(base, (i * 6, i * 6 + 4)),
            })

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 4: DEVICE-BASED MULE RING
# ============================================================================
def create_device_ring_scenario():
    transactions, devices, accounts = [], [], []

    mule_ring = [f"device_ring_{i}@upi" for i in range(1, 4)]
    shared_device = "device_fraud_ring_001"

    for acc in mule_ring:
        accounts.append({"account_id": acc, "account_age_days": np.random.randint(10, 40)})
        devices.append({"account_id": acc, "device_id": shared_device})

    base = BASE_TIME + timedelta(hours=1)
    for i, acc in enumerate(mule_ring):
        receiver = mule_ring[(i + 1) % len(mule_ring)]
        transactions.append({
            "sender": acc, "receiver": receiver,
            "amount": np.random.randint(8000, 20000),
            "timestamp": _rand_ts(base, (i * 2, i * 2 + 2)),
        })

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 5: RAPID ONBOARDING FRAUD
# ============================================================================
def create_rapid_onboarding_scenario():
    transactions, devices, accounts = [], [], []

    new_mule = "new_mule_account@upi"
    accounts.append({"account_id": new_mule, "account_age_days": 1})
    devices.append({"account_id": new_mule, "device_id": "device_burner_001"})

    base = BASE_TIME + timedelta(hours=0, minutes=30)
    # Bot-like burst — 8 receive txns in ~20 minutes
    for idx in range(8):
        src = f"source_{random.randint(1000, 9999)}@upi"
        transactions.append({
            "sender": src, "receiver": new_mule,
            "amount": np.random.randint(3000, 12000),
            "timestamp": (base + timedelta(minutes=idx * 2 + random.randint(0, 1),
                                           seconds=random.randint(0, 30))).isoformat(),
        })

    total_in = sum(t["amount"] for t in transactions if t["receiver"] == new_mule)
    for idx in range(5):
        transactions.append({
            "sender": new_mule,
            "receiver": f"cash_out_{random.randint(1000, 9999)}@upi",
            "amount": int(total_in * 0.18),
            "timestamp": (base + timedelta(minutes=25 + idx * 3)).isoformat(),
        })

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 6: NIGHT-TIME SMURFING (Structuring + odd hours)
# ============================================================================
def create_smurfing_scenario():
    transactions, devices, accounts = [], [], []

    smurf_acc = "smurf_master@upi"
    accounts.append({"account_id": smurf_acc, "account_age_days": 60})
    devices.append({"account_id": smurf_acc, "device_id": "device_smurf_001"})

    # Night-time small transactions to stay under radar
    base = datetime(2026, 2, 10, 1, 0, 0)  # 1 AM
    for i in range(12):
        target = f"smurf_target_{i}@upi"
        transactions.append({
            "sender": smurf_acc, "receiver": target,
            "amount": np.random.randint(900, 2000),  # Structuring: stay small
            "timestamp": (base + timedelta(minutes=i * 8 + random.randint(0, 5))).isoformat(),
        })
        if i < 6:
            accounts.append({"account_id": target, "account_age_days": np.random.randint(100, 400)})
            devices.append({"account_id": target, "device_id": f"device_st_{i}"})

    return transactions, accounts, devices


# ============================================================================
# SCENARIO 7: MULTI-DEVICE SPOOFING
# ============================================================================
def create_multi_device_scenario():
    transactions, devices, accounts = [], [], []

    spoofer = "spoofer_account@upi"
    accounts.append({"account_id": spoofer, "account_age_days": 15})

    # Same account, 6 different devices
    for d in range(6):
        devices.append({"account_id": spoofer, "device_id": f"spoofed_device_{d:03d}"})

    base = BASE_TIME + timedelta(hours=10)
    for i in range(6):
        transactions.append({
            "sender": f"victim_{random.randint(100, 999)}@upi",
            "receiver": spoofer,
            "amount": np.random.randint(4000, 15000),
            "timestamp": _rand_ts(base, (i, i + 2)),
        })

    return transactions, accounts, devices


# ============================================================================
# LEGITIMATE BACKGROUND TRAFFIC
# ============================================================================
def create_legitimate_background_traffic(num_accounts=20):
    transactions, devices, accounts = [], [], []

    for i in range(num_accounts):
        acc = f"legitimate_{i}@upi"
        accounts.append({"account_id": acc, "account_age_days": np.random.randint(100, 900)})
        devices.append({"account_id": acc, "device_id": f"device_{i}"})

    base = BASE_TIME - timedelta(hours=24)
    for _ in range(40):
        s_idx = random.randint(0, num_accounts - 1)
        r_idx = random.randint(0, num_accounts - 1)
        if s_idx == r_idx:
            continue
        transactions.append({
            "sender": f"legitimate_{s_idx}@upi",
            "receiver": f"legitimate_{r_idx}@upi",
            "amount": np.random.randint(200, 5000),
            "timestamp": _rand_ts(base, (0, 72), 60),  # Spread over 3 days
        })

    return transactions, accounts, devices


# ============================================================================
# MAIN GENERATOR
# ============================================================================
def generate_enhanced_dataset():
    all_txns, all_accounts, all_devices = [], [], []

    scenarios = [
        ("Star Aggregator", create_star_aggregator_scenario),
        ("Circular Network", create_circular_network_scenario),
        ("Chain Laundering", create_chain_laundering_scenario),
        ("Device Ring", create_device_ring_scenario),
        ("Rapid Onboarding", create_rapid_onboarding_scenario),
        ("Night Smurfing", create_smurfing_scenario),
        ("Multi-Device Spoofing", create_multi_device_scenario),
        ("Legitimate Traffic", lambda: create_legitimate_background_traffic(25)),
    ]

    for name, fn in scenarios:
        txns, accs, devs = fn()
        all_txns.extend(txns)
        all_accounts.extend(accs)
        all_devices.extend(devs)
        print(f"  \u2705 {name}: {len(txns)} txns, {len(accs)} accounts")

    txns_df = pd.DataFrame(all_txns)
    accounts_df = pd.DataFrame(all_accounts).drop_duplicates(subset=["account_id"], keep="first").reset_index(drop=True)
    devices_df = pd.DataFrame(all_devices).drop_duplicates(subset=["account_id", "device_id"], keep="first").reset_index(drop=True)
    txns_df = txns_df.dropna().reset_index(drop=True)

    return txns_df, accounts_df, devices_df


if __name__ == "__main__":
    print("\U0001f680 Generating enhanced dataset with mule scenarios...\n")
    txns, accounts, devices = generate_enhanced_dataset()

    txns.to_csv("data/transactions.csv", index=False)
    accounts.to_csv("data/accounts.csv", index=False)
    devices.to_csv("data/devices.csv", index=False)

    print(f"\n\U0001f4ca Dataset Summary:")
    print(f"  \u2022 Transactions: {len(txns)}")
    print(f"  \u2022 Unique Accounts: {len(accounts)}")
    print(f"  \u2022 Device Mappings: {len(devices)}")
    print(f"\n\u2705 Saved to data/ directory")
    print(f"\n\U0001f3af Known Mule Accounts:")
    print(f"  \u2022 mule_aggregator@upi   (Star pattern)")
    print(f"  \u2022 circle_node_*@upi     (Circular)")
    print(f"  \u2022 chain_node_*@upi      (Laundering chain)")
    print(f"  \u2022 device_ring_*@upi     (Device ring)")
    print(f"  \u2022 new_mule_account@upi  (Rapid onboarding)")
    print(f"  \u2022 smurf_master@upi      (Night smurfing)")
    print(f"  \u2022 spoofer_account@upi   (Multi-device)")
