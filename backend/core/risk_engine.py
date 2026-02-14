"""
Risk aggregation and decision engine for UPI account scoring.
Combines multiple risk signals and provides actionable recommendations.
"""

from typing import Literal


def aggregate_risk(
    behavioral: float,
    graph: float,
    device: float,
    temporal: float = 0.0,
    ml_anomaly: float = 0.0
) -> int:
    """
    Advanced risk aggregation with multi-signal correlation boosting.
    
    Weights (5-factor model - tuned for mule detection):
      Graph      = 35%  (structural patterns: stars, chains, rings)
      Behavioral = 35%  (velocity, flow patterns, amount anomalies)
      ML         = 15%  (unsupervised anomaly detection)
      Device     = 10%  (device fingerprinting)
      Temporal   = 5%   (time-based anomalies)
      
    Args:
        behavioral: Behavioral risk score (0-100)
        graph: Graph analysis risk score (0-100)
        device: Device risk score (0-100)
        temporal: Temporal risk score (0-100, default 0)
        ml_anomaly: ML anomaly score (0-100, default 0)
        
    Returns:
        Aggregated risk score (0-100)
    """

    # Base weighted score with adjusted weights
    base_score = (
        0.35 * behavioral
        + 0.35 * graph
        + 0.15 * ml_anomaly
        + 0.10 * device
        + 0.05 * temporal
    )

    # CONFIDENCE BOOSTING: When multiple independent signals align
    boost: float = 0.0
    active_signals = sum([
        behavioral >= 15,  # Lowered from 25
        graph >= 15,       # Lowered from 25
        device >= 10,      # Lowered from 15
        temporal >= 10,    # Lowered from 20
        ml_anomaly >= 30,  # Lowered from 40
    ])

    # Multi-signal agreement
    if active_signals >= 4:
        boost += 15  # Reduced from 20
    elif active_signals >= 3:
        boost += 12  # Reduced from 15
    elif active_signals >= 2:
        boost += 6   # Reduced from 8

    # Strong pair correlations
    if graph >= 20 and device >= 10:  # Lowered thresholds
        boost += 8

    if behavioral >= 20 and graph >= 20:  # Lowered thresholds
        boost += 6

    # Extreme signal correlation
    if behavioral >= 30 and graph >= 30 and device >= 20:
        boost += 10

    final_score = min(base_score + boost, 100)

    return int(final_score)


def risk_level(score: float) -> Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
    """
    Risk classification with sensitive thresholds for mule detection:
    - CRITICAL: 75+ (strong mule indicators, immediate action)
    - HIGH: 50-74 (multiple suspicious patterns detected)
    - MEDIUM: 25-49 (some indicators present, needs monitoring)
    - LOW: <25 (likely legitimate activity)
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Risk level classification
    """
    if score >= 75:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 25:
        return "MEDIUM"
    else:
        return "LOW"


def get_risk_confidence(score: float) -> Literal["VERY HIGH", "HIGH", "MODERATE", "LOW", "MINIMAL"]:
    """
    Returns confidence level based on score height and separation.
    Helps interpret how certain the mule detection is.
    
    Args:
        score: Risk score (0-100)
        
    Returns:
        Confidence level
    """
    if score >= 85:
        return "VERY HIGH"
    elif score >= 70:
        return "HIGH"
    elif score >= 50:
        return "MODERATE"
    elif score >= 40:
        return "LOW"
    else:
        return "MINIMAL"


def get_recommended_action(risk_lvl: str) -> str:
    """
    Return recommended action based on risk level.
    
    Args:
        risk_lvl: Risk level classification
        
    Returns:
        Recommended action string
    """
    actions = {
        "CRITICAL": "BLOCK IMMEDIATELY - Freeze account, alert compliance, file SAR",
        "HIGH": "INVESTIGATE - Manual review within 24h, enhanced monitoring",
        "MEDIUM": "MONITOR - Add to watchlist, flag for periodic review",
        "LOW": "ALLOW - Normal operations, routine monitoring",
    }
    return actions.get(risk_lvl, "MONITOR")
