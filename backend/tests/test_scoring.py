from backend.api.score import score_account
from backend.utils.data_loader import load_transactions, load_accounts, load_devices
from backend.core.graph_analysis import build_transaction_graph


def test_score_account_valid():
    txns = load_transactions()
    accounts = load_accounts()
    devices = load_devices()
    G = build_transaction_graph(txns)
    result = score_account("ACC001", txns, accounts, devices, G)
    assert isinstance(result, dict)
    assert "risk_score" in result
    assert 0 <= result["risk_score"] <= 100


def test_score_account_invalid():
    txns = load_transactions()
    accounts = load_accounts()
    devices = load_devices()
    G = build_transaction_graph(txns)
    result = score_account("INVALID_ACC", txns, accounts, devices, G)
    assert result["risk_level"] == "LOW" or result["risk_score"] == 0
