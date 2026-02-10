def aggregate_risk(behavioral, graph, device):
    """
    Strongly prioritize graph-based mule patterns
    """
    score = (
        0.3 * behavioral +
        0.5 * graph +      # increased weight
        0.2 * device
    )

    # BOOST: correlated mule signals
    if graph >= 30 and device >= 20:
        score += 20

    return min(int(score), 100)

def risk_level(score):
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"