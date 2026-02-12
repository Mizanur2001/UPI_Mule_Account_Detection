import networkx as nx
from collections import deque


def build_transaction_graph(df):
    """Build directed graph from transaction DataFrame (vectorized, no iterrows)."""
    G = nx.from_pandas_edgelist(
        df,
        source="sender",
        target="receiver",
        edge_attr="amount",
        create_using=nx.DiGraph(),
    )
    return G


# ---------------------------------------------------------------------------
# Efficient cycle detection  – replaces nx.simple_cycles (exponential)
# Uses DFS with a depth cap; returns the *set* of nodes that participate
# in at least one short cycle (length 3-6).  O(V * depth_limit) worst-case.
# ---------------------------------------------------------------------------
def _find_cycle_members(G, max_len=6):
    """Return a set of nodes that belong to at least one cycle of length <= max_len."""
    cycle_members = set()
    nodes = list(G.nodes())
    for start in nodes:
        # DFS stack: (current_node, path_so_far)
        stack = [(start, [start])]
        visited_from_start = set()
        while stack:
            node, path = stack.pop()
            if len(path) > max_len:
                continue
            for succ in G.successors(node):
                if succ == start and len(path) >= 3:
                    # Found a cycle back to start
                    cycle_members.update(path)
                    # No need to keep searching from this start
                    stack.clear()
                    break
                if succ not in visited_from_start and succ != start:
                    visited_from_start.add(succ)
                    stack.append((succ, path + [succ]))
            else:
                continue
            break  # inner break propagated
    return cycle_members


# ---------------------------------------------------------------------------
# BFS-based chain detection – replaces nx.all_simple_paths (exponential)
# Just checks whether a chain of length >= 4 exists from `account`.
# ---------------------------------------------------------------------------
def _has_chain(G, account, min_len=4, max_depth=5):
    """Return True if a simple path of length >= min_len starts from account (BFS, depth-limited)."""
    # BFS with path tracking (depth-limited so it's bounded)
    queue = deque([(account, {account})])  # (current_node, visited_set)
    while queue:
        node, visited = queue.popleft()
        if len(visited) >= min_len:
            return True
        if len(visited) >= max_depth:
            continue
        for succ in G.successors(node):
            if succ not in visited:
                queue.append((succ, visited | {succ}))
    return False


# ---------------------------------------------------------------------------
# Batch scoring – compute graph risk for ALL accounts at once
# ---------------------------------------------------------------------------
def batch_graph_risk(G):
    """
    Returns dict  {account_id: (score, [reasons])}  for every node in G.
    Runs the expensive cycle detection ONCE, then scores each node in O(1).
    Enhanced with detailed pattern metrics.
    """
    cycle_members = _find_cycle_members(G, max_len=6)
    results = {}

    for account in G.nodes():
        score = 0
        reasons = []

        in_deg = G.in_degree(account)
        out_deg = G.out_degree(account)

        # STAR PATTERN: Multiple inflows → single outflow (classic mule aggregator)
        if in_deg >= 5 and out_deg == 1:
            score += 45
            reasons.append(f"Strong star aggregator pattern ({in_deg} inflows → 1 outflow)")
        elif in_deg >= 3 and out_deg == 1:
            score += 30
            reasons.append(f"Star-pattern mule behavior ({in_deg} inflows → 1 outflow)")
        elif in_deg >= 2 and out_deg == 1:
            score += 15
            reasons.append(f"Possible aggregator ({in_deg} inflows → 1 outflow)")

        # REVERSE STAR: Single inflow → multiple outflows (classic money distributor)
        if out_deg >= 5 and in_deg == 1:
            score += 45
            reasons.append(f"Strong money distributor pattern (1 inflow → {out_deg} outflows)")
        elif out_deg >= 3 and in_deg == 1:
            score += 30
            reasons.append(f"Distributor pattern (1 inflow → {out_deg} outflows)")

        # BALANCED FLOW: Both high in/out degrees (relay node in processing network)
        if in_deg >= 3 and out_deg >= 3 and in_deg >= 2 * out_deg:
            score += 35
            reasons.append(f"Relay/processing node ({in_deg} inflows → {out_deg} outflows)")

        # CHAIN PATTERN: Account part of money laundering chain
        if out_deg > 0 and _has_chain(G, account):
            # Check chain depth
            if _has_chain(G, account, min_len=6, max_depth=8):
                score += 35
                reasons.append("Deep money laundering chain detected (4+ hops)")
            elif _has_chain(G, account, min_len=5, max_depth=7):
                score += 30
                reasons.append("Extended laundering chain (3+ hops)")
            else:
                score += 20
                reasons.append("Part of money laundering chain")

        # CIRCULAR PATTERN: Account in mule network loop
        if account in cycle_members:
            score += 50
            reasons.append("Part of circular mule network (fund rotation)")

        results[account] = (min(int(score), 100), reasons)

    return results


def graph_risk(account, G, precomputed_cycles=None, _batch_cache=None):
    """
    Single-account entry point (kept for backward-compat).
    Prefer batch_graph_risk() for bulk scoring.
    """
    # If caller provides a pre-computed batch cache, use it
    if _batch_cache is not None and account in _batch_cache:
        return _batch_cache[account]

    score = 0
    reasons = []

    try:
        if account not in G:
            return 0, []

        in_deg = G.in_degree(account)
        out_deg = G.out_degree(account)

        if in_deg >= 3 and out_deg == 1:
            score += 30
            reasons.append("Star-pattern mule behavior")

        if out_deg > 0 and _has_chain(G, account):
            score += 25
            reasons.append("Chain money laundering pattern")

        if precomputed_cycles is not None:
            for cycle in precomputed_cycles:
                if account in cycle and len(cycle) >= 3:
                    score += 50
                    reasons.append("Circular mule network detected")
                    break
        else:
            cycle_members = _find_cycle_members(G, max_len=6)
            if account in cycle_members:
                score += 50
                reasons.append("Circular mule network detected")

    except Exception:
        pass

    return min(score, 100), reasons