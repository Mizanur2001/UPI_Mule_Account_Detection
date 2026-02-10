from backend.utils.data_loader import *
from backend.core.behavioral import behavioral_risk
from backend.core.graph_analysis import build_transaction_graph, graph_risk, batch_graph_risk
from backend.core.device_risk import device_risk
from backend.core.risk_engine import aggregate_risk, risk_level

def score_account(account_id, txns=None, accounts=None, devices=None, G=None, cycles=None, _graph_cache=None):
    if txns is None:
        txns = load_transactions()
    if accounts is None:
        accounts = load_accounts()
    if devices is None:
        devices = load_devices()

    # Handle case where account_id might not be in txns (though unlikely if called from dashboard list)
    # But filtering is okay.
    account_txns = txns[(txns["sender"] == account_id) | (txns["receiver"] == account_id)]
    
    # Handle missing account metadata safely
    account_meta_rows = accounts[accounts["account_id"] == account_id]
    if not account_meta_rows.empty:
        account_meta = account_meta_rows.iloc[0]
        behavioral_score, b_reasons = behavioral_risk(account_txns, account_meta)
    else:
        # Default if not found
        behavioral_score, b_reasons = 0, ["Account metadata not found"]

    if G is None:
        G = build_transaction_graph(txns)

    # Use batch cache if provided (avoids re-running expensive graph algos)
    if _graph_cache is not None and account_id in _graph_cache:
        graph_score, g_reasons = _graph_cache[account_id]
    else:
        graph_score, g_reasons = graph_risk(account_id, G, precomputed_cycles=cycles)

    device_score, d_reasons = device_risk(account_id, devices)

    final_score = aggregate_risk(behavioral_score, graph_score, device_score)

    return {
        "account_id": account_id,
        "risk_score": final_score,
        "risk_level": risk_level(final_score),
        "reasons": b_reasons + g_reasons + d_reasons
    }


def batch_score_accounts(account_ids, txns, accounts, devices, G):
    """
    Score all accounts in one pass.  Graph analysis runs ONCE for the
    entire graph, then each account just does a dict lookup.
    Returns dict {account_id: score_result_dict}
    """
    graph_cache = batch_graph_risk(G)
    results = {}
    for acc in account_ids:
        results[acc] = score_account(
            acc,
            txns=txns,
            accounts=accounts,
            devices=devices,
            G=G,
            _graph_cache=graph_cache,
        )
    return results
