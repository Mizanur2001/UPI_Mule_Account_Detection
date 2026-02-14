"""
Temporal Analysis Module - Time-based anomaly detection for UPI mule accounts.
Detects suspicious temporal patterns like burst transactions, odd-hour activity,
and velocity spikes that indicate automated or coordinated fraud.
"""

from typing import Tuple, List, Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def temporal_risk(account_id: str, account_txns: pd.DataFrame) -> Tuple[float, List[str]]:
    """
    Analyze time-based patterns for mule detection.
    
    Args:
        account_id: Account ID to analyze
        account_txns: DataFrame of account transactions
        
    Returns:
        Tuple of (risk_score: 0-100, reasons: list of explanation strings)
    """
    score: float = 0.0
    reasons: List[str] = []

    if len(account_txns) < 2:
        return 0.0, []

    # Parse timestamps if present
    if "timestamp" not in account_txns.columns:
        return 0.0, []

    try:
        txns = account_txns.copy()
        txns["timestamp"] = pd.to_datetime(txns["timestamp"], errors="coerce")
        txns = txns.dropna(subset=["timestamp"]).sort_values("timestamp")

        if len(txns) < 2:
            return 0.0, []

        # ── 1. BURST DETECTION ──────────────────────────────────────────
        # Multiple transactions in very short time windows (< 5 minutes)
        time_diffs = txns["timestamp"].diff().dt.total_seconds().dropna()

        if len(time_diffs) > 0:
            burst_count = (time_diffs < 300).sum()  # Under 5 min
            rapid_count = (time_diffs < 60).sum()    # Under 1 min

            if rapid_count >= 3:
                score += 35
                reasons.append(
                    f"Rapid-fire burst: {rapid_count} transactions within 60 seconds (bot-like)"
                )
            elif burst_count >= 3:
                score += 25
                reasons.append(
                    f"Burst pattern: {burst_count} transactions within 5-minute windows"
                )

        # ── 2. ODD-HOUR ACTIVITY ────────────────────────────────────────
        # Transactions between 12 AM - 5 AM (suspicious for P2P)
        hours = txns["timestamp"].dt.hour
        night_txns = ((hours >= 0) & (hours < 5)).sum()
        night_pct = night_txns / len(txns) if len(txns) > 0 else 0

        if night_pct > 0.5 and night_txns >= 3:
            score += 30
            reasons.append(
                f"Predominantly night-time activity: {night_txns}/{len(txns)} "
                f"transactions between 12AM-5AM ({night_pct:.0%})"
            )
        elif night_txns >= 2:
            score += 15
            reasons.append(
                f"Suspicious night activity: {night_txns} transactions between 12AM-5AM"
            )

        # ── 3. VELOCITY SPIKE DETECTION ─────────────────────────────────
        # Compare recent vs historical activity rate
        if len(txns) >= 4:
            total_span = (txns["timestamp"].max() - txns["timestamp"].min()).total_seconds()
            if total_span > 0:
                # Split into first half and second half
                mid_idx = len(txns) // 2
                first_half = txns.iloc[:mid_idx]
                second_half = txns.iloc[mid_idx:]

                span_first = (first_half["timestamp"].max() - first_half["timestamp"].min()).total_seconds()
                span_second = (second_half["timestamp"].max() - second_half["timestamp"].min()).total_seconds()

                if span_first > 0 and span_second > 0:
                    rate_first = len(first_half) / (span_first / 3600)   # txn/hour
                    rate_second = len(second_half) / (span_second / 3600)  # txn/hour

                    if rate_second > rate_first * 3 and rate_second > 2:
                        score += 25
                        reasons.append(
                            f"Velocity spike: rate jumped from {rate_first:.1f} to "
                            f"{rate_second:.1f} txns/hr ({rate_second/max(rate_first,0.1):.1f}x increase)"
                        )

        # ── 4. WEEKEND/HOLIDAY CONCENTRATION ────────────────────────────
        weekday_counts = txns["timestamp"].dt.dayofweek
        weekend_txns = (weekday_counts >= 5).sum()
        weekend_pct = weekend_txns / len(txns) if len(txns) > 0 else 0

        if weekend_pct > 0.7 and weekend_txns >= 4:
            score += 15
            reasons.append(
                f"Heavy weekend concentration: {weekend_pct:.0%} of transactions on weekends"
            )

        # ── 5. UNIFORM TIME SPACING (Bot signature) ────────────────────
        if len(time_diffs) >= 4:
            std_dev = time_diffs.std()
            mean_diff = time_diffs.mean()
            if mean_diff > 0:
                cv = std_dev / mean_diff  # Coefficient of variation
                if cv < 0.15 and mean_diff < 600:
                    score += 30
                    reasons.append(
                        f"Suspiciously uniform timing (CV={cv:.2f}): "
                        f"avg {mean_diff:.0f}s between transactions – automated behavior"
                    )
                elif cv < 0.3 and mean_diff < 300:
                    score += 20
                    reasons.append(
                        f"Near-uniform timing pattern (CV={cv:.2f}): possible automation"
                    )

    except Exception:
        pass

    return min(int(score), 100), reasons


def compute_transaction_velocity(
    account_id: str,
    txns: pd.DataFrame,
    window_hours: int = 1
) -> Dict[str, float]:
    """
    Compute velocity metrics for an account within a sliding window.
    Used for real-time monitoring dashboards.
    
    Args:
        account_id: Account ID to analyze
        txns: DataFrame of all transactions
        window_hours: Sliding window size in hours
        
    Returns:
        Dictionary with velocity metrics
    """
    account_txns = txns[
        (txns["sender"] == account_id) | (txns["receiver"] == account_id)
    ].copy()

    if "timestamp" not in account_txns.columns or len(account_txns) == 0:
        return {"txn_count": len(account_txns), "velocity_per_hour": 0.0, "peak_velocity": 0}

    account_txns["timestamp"] = pd.to_datetime(account_txns["timestamp"], errors="coerce")
    account_txns = account_txns.dropna(subset=["timestamp"]).sort_values("timestamp")

    if len(account_txns) < 2:
        return {"txn_count": len(account_txns), "velocity_per_hour": 0.0, "peak_velocity": 0}

    total_span_hours = (
        account_txns["timestamp"].max() - account_txns["timestamp"].min()
    ).total_seconds() / 3600

    avg_velocity = len(account_txns) / max(total_span_hours, 0.01)

    # Peak velocity in sliding window
    peak_velocity = 0
    window = pd.Timedelta(hours=window_hours)
    for i, row in account_txns.iterrows():
        window_end = row["timestamp"] + window
        count_in_window = (
            (account_txns["timestamp"] >= row["timestamp"])
            & (account_txns["timestamp"] <= window_end)
        ).sum()
        peak_velocity = max(peak_velocity, count_in_window)

    return {
        "txn_count": len(account_txns),
        "velocity_per_hour": round(avg_velocity, 2),
        "peak_velocity": int(peak_velocity),
        "time_span_hours": round(total_span_hours, 2),
    }

    """
    Analyze time-based patterns for mule detection.
    Returns (score: int, reasons: list[str])
    """
    score = 0
    reasons = []

    if len(account_txns) < 2:
        return 0, []

    # Parse timestamps if present
    if "timestamp" not in account_txns.columns:
        return 0, []

    try:
        txns = account_txns.copy()
        txns["timestamp"] = pd.to_datetime(txns["timestamp"], errors="coerce")
        txns = txns.dropna(subset=["timestamp"]).sort_values("timestamp")

        if len(txns) < 2:
            return 0, []

        # ── 1. BURST DETECTION ──────────────────────────────────────────
        # Multiple transactions in very short time windows (< 5 minutes)
        time_diffs = txns["timestamp"].diff().dt.total_seconds().dropna()

        if len(time_diffs) > 0:
            burst_count = (time_diffs < 300).sum()  # Under 5 min
            rapid_count = (time_diffs < 60).sum()    # Under 1 min

            if rapid_count >= 3:
                score += 35
                reasons.append(
                    f"Rapid-fire burst: {rapid_count} transactions within 60 seconds (bot-like)"
                )
            elif burst_count >= 3:
                score += 25
                reasons.append(
                    f"Burst pattern: {burst_count} transactions within 5-minute windows"
                )

        # ── 2. ODD-HOUR ACTIVITY ────────────────────────────────────────
        # Transactions between 12 AM - 5 AM (suspicious for P2P)
        hours = txns["timestamp"].dt.hour
        night_txns = ((hours >= 0) & (hours < 5)).sum()
        night_pct = night_txns / len(txns) if len(txns) > 0 else 0

        if night_pct > 0.5 and night_txns >= 3:
            score += 30
            reasons.append(
                f"Predominantly night-time activity: {night_txns}/{len(txns)} "
                f"transactions between 12AM-5AM ({night_pct:.0%})"
            )
        elif night_txns >= 2:
            score += 15
            reasons.append(
                f"Suspicious night activity: {night_txns} transactions between 12AM-5AM"
            )

        # ── 3. VELOCITY SPIKE DETECTION ─────────────────────────────────
        # Compare recent vs historical activity rate
        if len(txns) >= 4:
            total_span = (txns["timestamp"].max() - txns["timestamp"].min()).total_seconds()
            if total_span > 0:
                # Split into first half and second half
                mid_idx = len(txns) // 2
                first_half = txns.iloc[:mid_idx]
                second_half = txns.iloc[mid_idx:]

                span_first = (first_half["timestamp"].max() - first_half["timestamp"].min()).total_seconds()
                span_second = (second_half["timestamp"].max() - second_half["timestamp"].min()).total_seconds()

                if span_first > 0 and span_second > 0:
                    rate_first = len(first_half) / (span_first / 3600)   # txn/hour
                    rate_second = len(second_half) / (span_second / 3600)  # txn/hour

                    if rate_second > rate_first * 3 and rate_second > 2:
                        score += 25
                        reasons.append(
                            f"Velocity spike: rate jumped from {rate_first:.1f} to "
                            f"{rate_second:.1f} txns/hr ({rate_second/max(rate_first,0.1):.1f}x increase)"
                        )

        # ── 4. WEEKEND/HOLIDAY CONCENTRATION ────────────────────────────
        weekday_counts = txns["timestamp"].dt.dayofweek
        weekend_txns = (weekday_counts >= 5).sum()
        weekend_pct = weekend_txns / len(txns) if len(txns) > 0 else 0

        if weekend_pct > 0.7 and weekend_txns >= 4:
            score += 15
            reasons.append(
                f"Heavy weekend concentration: {weekend_pct:.0%} of transactions on weekends"
            )

        # ── 5. UNIFORM TIME SPACING (Bot signature) ────────────────────
        if len(time_diffs) >= 4:
            std_dev = time_diffs.std()
            mean_diff = time_diffs.mean()
            if mean_diff > 0:
                cv = std_dev / mean_diff  # Coefficient of variation
                if cv < 0.15 and mean_diff < 600:
                    score += 30
                    reasons.append(
                        f"Suspiciously uniform timing (CV={cv:.2f}): "
                        f"avg {mean_diff:.0f}s between transactions – automated behavior"
                    )
                elif cv < 0.3 and mean_diff < 300:
                    score += 20
                    reasons.append(
                        f"Near-uniform timing pattern (CV={cv:.2f}): possible automation"
                    )

    except Exception:
        pass

    return min(int(score), 100), reasons


def compute_transaction_velocity(account_id: str, txns: pd.DataFrame, window_hours: int = 1) -> dict:
    """
    Compute velocity metrics for an account within a sliding window.
    Used for real-time monitoring dashboards.
    """
    account_txns = txns[
        (txns["sender"] == account_id) | (txns["receiver"] == account_id)
    ].copy()

    if "timestamp" not in account_txns.columns or len(account_txns) == 0:
        return {"txn_count": len(account_txns), "velocity_per_hour": 0, "peak_velocity": 0}

    account_txns["timestamp"] = pd.to_datetime(account_txns["timestamp"], errors="coerce")
    account_txns = account_txns.dropna(subset=["timestamp"]).sort_values("timestamp")

    if len(account_txns) < 2:
        return {"txn_count": len(account_txns), "velocity_per_hour": 0, "peak_velocity": 0}

    total_span_hours = (
        account_txns["timestamp"].max() - account_txns["timestamp"].min()
    ).total_seconds() / 3600

    avg_velocity = len(account_txns) / max(total_span_hours, 0.01)

    # Peak velocity in sliding window
    peak_velocity = 0
    window = pd.Timedelta(hours=window_hours)
    for i, row in account_txns.iterrows():
        window_end = row["timestamp"] + window
        count_in_window = (
            (account_txns["timestamp"] >= row["timestamp"])
            & (account_txns["timestamp"] <= window_end)
        ).sum()
        peak_velocity = max(peak_velocity, count_in_window)

    return {
        "txn_count": len(account_txns),
        "velocity_per_hour": round(avg_velocity, 2),
        "peak_velocity": int(peak_velocity),
        "time_span_hours": round(total_span_hours, 2),
    }
