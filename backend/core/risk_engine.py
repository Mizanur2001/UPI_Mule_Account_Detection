def aggregate_risk(behavioral, graph, device):
    """
    Advanced risk aggregation with multi-signal correlation boosting.
    Weights: Graph (50%) > Behavioral (30%) > Device (20%)
    Applies confidence amplification when multiple signals align.
    """
    
    # Base weighted score
    base_score = (
        0.30 * behavioral +
        0.50 * graph +
        0.20 * device
    )
    
    # CONFIDENCE BOOSTING: When multiple independent signals align
    boost = 0
    
    # Correlation boosts for strong mule indicators
    if graph >= 30 and device >= 15:  # Graph + Device alignment
        boost += 15
    
    if behavioral >= 30 and graph >= 30:  # Behavioral + Graph alignment
        boost += 12
    
    if behavioral >= 25 and device >= 20:  # All three signals present
        boost += 10
    
    # Extreme signal correlation
    if behavioral >= 40 and graph >= 40 and device >= 30:
        boost += 15
    
    # Apply boost
    final_score = min(base_score + boost, 100)
    
    return int(final_score)


def risk_level(score):
    """
    Risk classification with clear thresholds:
    - HIGH: 70+ (strong mule indicators, needs investigation)
    - MEDIUM: 40-69 (suspicious patterns, monitor)
    - LOW: <40 (likely legitimate)
    """
    if score >= 70:
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
    if score >= 80:
        return "VERY HIGH"
    elif score >= 70:
        return "HIGH"
    elif score >= 50:
        return "MODERATE"
    elif score >= 40:
        return "LOW"
    else:
        return "MINIMAL"