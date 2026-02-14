"""
Behavioral risk analysis for UPI accounts.
Detects anomalies in transaction velocity, flow patterns, and amounts.
"""

from typing import Tuple, List
import pandas as pd


def behavioral_risk(account_txns: pd.DataFrame, account_meta: pd.Series) -> Tuple[float, List[str]]:
    """
    Detects velocity & temporal anomalies with detailed metrics.
    
    Args:
        account_txns: DataFrame of transactions for this account
        account_meta: Series with account metadata (account_age_days, etc.)
        
    Returns:
        Tuple of (risk_score: 0-100, reasons: list of explanation strings)
    """
    score: float = 0.0
    reasons: List[str] = []
    
    if len(account_txns) == 0:
        return 0.0, []

    txn_count = len(account_txns)
    avg_amount = account_txns["amount"].mean() if txn_count else 0.0
    max_amount = account_txns["amount"].max() if txn_count else 0.0
    total_volume = account_txns["amount"].sum() if txn_count else 0.0
    
    # Extract sender and receiver transactions
    sent_txns = account_txns[account_txns["sender"] == account_meta["account_id"]]
    recv_txns = account_txns[account_txns["receiver"] == account_meta["account_id"]]
    
    sent_count = len(sent_txns)
    recv_count = len(recv_txns)

    # VELOCITY DETECTION
    if txn_count >= 10:
        score += 25
        reasons.append(f"Very high transaction velocity ({txn_count} txns)")
    elif txn_count >= 5:
        score += 15
        reasons.append(f"High transaction velocity ({txn_count} txns)")
    elif txn_count >= 3:
        score += 8
        reasons.append(f"Moderate transaction velocity ({txn_count} txns)")

    # ASYMMETRIC FLOW (Classic mule indicator: sends out most of what comes in)
    if recv_count >= 3 and sent_count >= 3:
        inflow = recv_txns["amount"].sum()
        outflow = sent_txns["amount"].sum()
        if inflow > 0:
            pass_through_ratio = outflow / inflow
            if 0.8 <= pass_through_ratio <= 1.2:  # 80-120% pass-through
                score += 45
                reasons.append(f"STRONG MULE PATTERN: {pass_through_ratio:.1%} pass-through ratio (inflow→outflow)")
            elif 0.5 <= pass_through_ratio <= 1.5 and inflow > 1000:
                score += 30
                reasons.append(f"Mule pattern: {pass_through_ratio:.1%} pass-through with high inflow")
            elif pass_through_ratio > 1.2:  # Sends more than received
                score += 20
                reasons.append(f"Outflow exceeds inflow (pass-through ratio: {pass_through_ratio:.1%})")

    # AMOUNT ANOMALIES
    if max_amount > 10000:
        score += 25
        reasons.append(f"Very large single transaction (₹{max_amount:,.0f})")
    elif max_amount > 8000:
        score += 15
        reasons.append(f"Large transaction detected (₹{max_amount:,.0f})")
    if avg_amount > 5000:
        score += 12
        reasons.append(f"High average transaction amount (₹{avg_amount:,.0f})")
    elif avg_amount > 3000:
        score += 6
        reasons.append(f"Moderate transaction amount (₹{avg_amount:,.0f})")
    
    if max_amount > 10000:
        score += 15
        reasons.append(f"Very large single transaction (₹{max_amount:,.0f})")

    # NEW ACCOUNT WITH RAPID ACTIVITY (Critical for onboarding fraud)
    account_age = account_meta.get("account_age_days", 0)
    if account_age < 7 and txn_count >= 2:
        score += 40
        reasons.append(f"Brand new account ({account_age} days old) with rapid activity")
    elif account_age < 30 and txn_count >= 3:
        score += 30
        reasons.append(f"New account ({account_age} days old) with {txn_count} transactions")
    elif account_age < 90 and txn_count >= 5:
        score += 15
        reasons.append(f"Young account ({account_age} days old) with high velocity")

    # TOTAL VOLUME SPIKE
    if total_volume > 50000:
        score += 20
        reasons.append(f"Large total transaction volume (₹{total_volume:,.0f})")

    # NO RECEIVING TRANSACTIONS (Pure sender is suspicious)
    if recv_count == 0 and sent_count >= 3:
        score += 20
        reasons.append("Account only sends money (no receiving transactions)")

    return min(int(score), 100), reasons
