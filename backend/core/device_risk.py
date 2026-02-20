# Scores risk from shared and rotating device fingerprints
def device_risk(account, device_df):
    score = 0
    reasons = []

    linked_accounts = device_df[device_df["account_id"] == account]
    
    if len(linked_accounts) == 0:
        return 0, ["No device data available"]

    device_ids = linked_accounts["device_id"].unique().tolist()
    
    shared_device_df = device_df[device_df["device_id"].isin(device_ids)]
    unique_accounts = shared_device_df["account_id"].unique()
    unique_accounts = [a for a in unique_accounts if a != account]
    
    accounts_on_shared_devices = len(unique_accounts)
    num_devices = len(device_ids)

    if accounts_on_shared_devices >= 10:
        score += 50
        reasons.append(f"Device shared across {accounts_on_shared_devices} other accounts (very high concentration)")
    elif accounts_on_shared_devices >= 5:
        score += 40
        reasons.append(f"Device shared across {accounts_on_shared_devices} other accounts")
    elif accounts_on_shared_devices >= 3:
        score += 30
        reasons.append(f"Shared device controlling {accounts_on_shared_devices} accounts (aggregator network)")
    elif accounts_on_shared_devices >= 2:
        score += 15
        reasons.append(f"Device linked to {accounts_on_shared_devices} other accounts")

    if num_devices >= 5:
        score += 30
        reasons.append(f"Account controlled from {num_devices} different devices (high rotation)")
    elif num_devices >= 3:
        score += 20
        reasons.append(f"Multiple device usage ({num_devices} devices) - possible spoofing")

    return min(int(score), 100), reasons
