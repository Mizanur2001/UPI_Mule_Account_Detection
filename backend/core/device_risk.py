def device_risk(account, device_df):
    score = 0
    reasons = []

    linked_accounts = device_df[device_df["account_id"] == account]

    device_ids = linked_accounts["device_id"].tolist()
    shared = device_df[device_df["device_id"].isin(device_ids)]

    unique_accounts = shared["account_id"].nunique()

    if unique_accounts >= 3:
        score += 40
        reasons.append("Shared device across multiple accounts")

    return min(score, 100), reasons