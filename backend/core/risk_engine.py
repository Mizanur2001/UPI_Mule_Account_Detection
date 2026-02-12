def aggregate_risk(behavioral, graph, device, temporal=0, ml_anomaly=0):
    """
    Advanced risk aggregation with multi-signal correlation boosting.
    
    Weights (5-factor model):
      Graph      = 40%  (strongest structural signal)
      Behavioral = 25%  (velocity & flow anomalies)
      Device     = 15%  (device fingerprinting)
      Temporal   = 10%  (time-based anomalies)
      ML         = 10%  (unsupervised anomaly detection)
    
    Applies confidence amplification when multiple independent signals align.
    """

    # Base weighted score
    base_score = (
        0.25 * behavioral
        + 0.40 * graph
        + 0.15 * device
        + 0.10 * temporal
        + 0.10 * ml_anomaly
    )

    # CONFIDENCE BOOSTING: When multiple independent signals align
    boost = 0
    active_signals = sum([
        behavioral >= 25,
        graph >= 25,
        device >= 15,
        temporal >= 20,
        ml_anomaly >= 40,
    ])

    # Multi-signal agreement
    if active_signals >= 4:
        boost += 20
    elif active_signals >= 3:
        boost += 15
    elif active_signals >= 2:
        boost += 8

    # Strong pair correlations
    if graph >= 30 and device >= 15:
        boost += 10

    if behavioral >= 30 and graph >= 30:
        boost += 8

    # Extreme signal correlation
    if behavioral >= 40 and graph >= 40 and device >= 30:
        boost += 12

    final_score = min(base_score + boost, 100)

    return int(final_score)


def risk_level(score):
    """
    Risk classification with clear thresholds:
    - CRITICAL: 85+ (immediate block/freeze)
    - HIGH: 70-84 (strong mule indicators, needs investigation)
    - MEDIUM: 40-69 (suspicious patterns, monitor)
    - LOW: <40 (likely legitimate)
    """
    if score >= 85:
        return "CRITICAL"
    elif score >= 70:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    else:
        return "LOW"


def get_risk_confidence(score):
    """
    Returns confidence level based on score height and separation.
    Helps interpret how certain the mule detection is.
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


def get_recommended_action(risk_lvl):
    """Return recommended action based on risk level."""
    actions = {
        "CRITICAL": "BLOCK IMMEDIATELY - Freeze account, alert compliance, file SAR",
        "HIGH": "INVESTIGATE - Manual review within 24h, enhanced monitoring",
        "MEDIUM": "MONITOR - Add to watchlist, flag for periodic review",
        "LOW": "ALLOW - Normal operations, routine monitoring",
    }
    return actions.get(risk_lvl, "MONITOR")