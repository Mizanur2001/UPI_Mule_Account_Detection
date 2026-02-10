import networkx as nx

def build_transaction_graph(df):
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row["sender"], row["receiver"], amount=row["amount"])
    return G


def graph_risk(account, G):
    score = 0
    reasons = []

    in_deg = G.in_degree(account)
    out_deg = G.out_degree(account)

    # Star pattern
    if in_deg >= 3 and out_deg == 1:
        score += 30
        reasons.append("Star-pattern mule behavior")

    # Chain pattern
    try:
        for path in nx.all_simple_paths(G, source=account, cutoff=4):
            if len(path) >= 4:
                score += 25
                reasons.append("Chain money laundering pattern")
                break
    except:
        pass

    # Circular pattern
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            if account in cycle and len(cycle) >= 3:
                score += 50
                reasons.append("Circular mule network detected")
                break
    except:
        pass

    return min(score, 100), reasons