from backend.utils.data_loader import *
from backend.core.behavioral import behavioral_risk
from backend.core.graph_analysis import build_transaction_graph, graph_risk, batch_graph_risk
from backend.core.device_risk import device_risk
from backend.core.temporal_analysis import temporal_risk
from backend.core.ml_anomaly import ml_anomaly_detection
from backend.core.risk_engine import aggregate_risk, risk_level, get_risk_confidence, get_recommended_action


# Runs all 5 signals and returns combined risk for one account
def score_account(account_id, txns=None, accounts=None, devices=None, G=None,
                  cycles=None, _graph_cache=None, _ml_cache=None):
    if txns is None:
        txns = load_transactions()
    if accounts is None:
        accounts = load_accounts()
    if devices is None:
        devices = load_devices()

    account_txns = txns[(txns["sender"] == account_id) | (txns["receiver"] == account_id)]

    account_meta_rows = accounts[accounts["account_id"] == account_id]
    if not account_meta_rows.empty:
        account_meta = account_meta_rows.iloc[0]
        behavioral_score, b_reasons = behavioral_risk(account_txns, account_meta)
    else:
        behavioral_score, b_reasons = 0, ["Account metadata not found"]

    if G is None:
        G = build_transaction_graph(txns)

    if _graph_cache is not None and account_id in _graph_cache:
        graph_score, g_reasons = _graph_cache[account_id]
    else:
        graph_score, g_reasons = graph_risk(account_id, G, precomputed_cycles=cycles)

    device_score, d_reasons = device_risk(account_id, devices)

    temporal_score, t_reasons = temporal_risk(account_id, account_txns)

    ml_score = 0
    ml_label = "N/A"
    if _ml_cache is not None and account_id in _ml_cache:
        ml_data = _ml_cache[account_id]
        ml_score = ml_data["anomaly_score"]
        ml_label = ml_data["anomaly_label"]

    final_score = aggregate_risk(behavioral_score, graph_score, device_score,
                                  temporal_score, ml_score)
    risk_lvl = risk_level(final_score)
    confidence = get_risk_confidence(final_score)
    action = get_recommended_action(risk_lvl)

    return {
        "account_id": account_id,
        "risk_score": final_score,
        "risk_level": risk_lvl,
        "confidence": confidence,
        "recommended_action": action,
        "behavioral_score": int(behavioral_score),
        "graph_score": int(graph_score),
        "device_score": int(device_score),
        "temporal_score": int(temporal_score),
        "ml_anomaly_score": round(ml_score, 1),
        "ml_anomaly_label": ml_label,
        "reasons": b_reasons + g_reasons + d_reasons + t_reasons,
        "signal_count": sum([
            behavioral_score >= 25,
            graph_score >= 25,
            device_score >= 15,
            temporal_score >= 20,
            ml_score >= 40,
        ]),
    }


# Batch-scores accounts with precomputed graph and ML caches
def batch_score_accounts(account_ids, txns, accounts, devices, G):
    graph_cache = batch_graph_risk(G)

    ml_cache = ml_anomaly_detection(list(account_ids), txns, accounts, devices)

    results = {}
    for acc in account_ids:
        results[acc] = score_account(
            acc,
            txns=txns,
            accounts=accounts,
            devices=devices,
            G=G,
            _graph_cache=graph_cache,
            _ml_cache=ml_cache,
        )
    return results
