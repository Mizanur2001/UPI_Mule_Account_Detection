def behavioral_risk(account_txns, account_meta):
    """
    Detects velocity & temporal anomalies
    """
    score = 0
    reasons = []

    txn_count = len(account_txns)
    avg_amount = account_txns["amount"].mean() if txn_count else 0

    if txn_count >= 5:
        score += 30
        reasons.append("High transaction velocity")

    if avg_amount > 4000:
        score += 20
        reasons.append("Unusual average transaction amount")

    if account_meta["account_age_days"] < 30 and txn_count >= 3:
        score += 25
        reasons.append("New account with rapid activity")

    return min(score, 100), reasons