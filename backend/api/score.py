from backend.utils.data_loader import *
from backend.core.behavioral import behavioral_risk
from backend.core.graph_analysis import build_transaction_graph, graph_risk
from backend.core.device_risk import device_risk
from backend.core.risk_engine import aggregate_risk, risk_level

def score_account(account_id):
    txns = load_transactions()
    accounts = load_accounts()
    devices = load_devices()

    account_txns = txns[(txns["sender"] == account_id) | (txns["receiver"] == account_id)]
    account_meta = accounts[accounts["account_id"] == account_id].iloc[0]

    behavioral_score, b_reasons = behavioral_risk(account_txns, account_meta)

    G = build_transaction_graph(txns)
    graph_score, g_reasons = graph_risk(account_id, G)

    device_score, d_reasons = device_risk(account_id, devices)

    final_score = aggregate_risk(behavioral_score, graph_score, device_score)

    return {
        "account_id": account_id,
        "risk_score": final_score,
        "risk_level": risk_level(final_score),
        "reasons": b_reasons + g_reasons + d_reasons
    }
