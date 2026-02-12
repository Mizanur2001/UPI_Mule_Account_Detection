"""
UPI Mule Account Detection — FastAPI Backend
Production-grade REST API for real-time mule risk scoring.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import time
import pandas as pd
from datetime import datetime

from backend.api.score import score_account, batch_score_accounts
from backend.utils.data_loader import load_transactions, load_accounts, load_devices
from backend.core.graph_analysis import build_transaction_graph

# ── App Setup ─────────────────────────────────────────────────────────
app = FastAPI(
    title="UPI Mule Detection API",
    description=(
        "Real-time mule account detection engine for UPI ecosystems. "
        "Combines graph analytics, behavioral profiling, device correlation, "
        "temporal analysis, and ML-based anomaly detection."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Preload data (startup cache) ─────────────────────────────────────
_cache = {}


def _get_data():
    if "txns" not in _cache:
        txns = load_transactions()
        txns["sender"] = txns["sender"].astype(str)
        txns["receiver"] = txns["receiver"].astype(str)
        _cache["txns"] = txns
        _cache["accounts"] = load_accounts()
        _cache["devices"] = load_devices()
        _cache["G"] = build_transaction_graph(txns)
    return _cache["txns"], _cache["accounts"], _cache["devices"], _cache["G"]


# ── Models ────────────────────────────────────────────────────────────
class TransactionSimulation(BaseModel):
    sender: str
    receiver: str
    amount: float


class BatchRequest(BaseModel):
    account_ids: List[str]


# ── Endpoints ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "UPI Mule Detection API",
        "version": "2.0.0",
        "status": "operational",
        "endpoints": [
            "/score/{account_id}",
            "/batch_score",
            "/health",
            "/stats",
            "/simulate",
            "/docs",
        ],
    }


@app.get("/health")
def health():
    txns, accounts, devices, G = _get_data()
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "transactions": len(txns),
            "accounts": len(accounts),
            "devices": len(devices),
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
        },
    }


@app.get("/score/{account_id}")
def score(account_id: str):
    """Score a single account for mule risk in real-time."""
    start = time.time()
    txns, accounts, devices, G = _get_data()

    result = score_account(account_id, txns=txns, accounts=accounts, devices=devices, G=G)
    result["response_time_ms"] = round((time.time() - start) * 1000, 2)
    result["timestamp"] = datetime.utcnow().isoformat()
    return result


@app.post("/batch_score")
def batch_score(req: BatchRequest):
    """Score multiple accounts in a single batch call."""
    start = time.time()
    txns, accounts, devices, G = _get_data()

    results = batch_score_accounts(req.account_ids, txns, accounts, devices, G)
    return {
        "results": results,
        "count": len(results),
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/stats")
def stats():
    """Get system-wide risk statistics."""
    txns, accounts, devices, G = _get_data()
    unique_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
    results = batch_score_accounts(unique_accounts, txns, accounts, devices, G)

    risk_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    total_score = 0
    for res in results.values():
        risk_counts[res["risk_level"]] = risk_counts.get(res["risk_level"], 0) + 1
        total_score += res["risk_score"]

    return {
        "total_accounts": len(unique_accounts),
        "total_transactions": len(txns),
        "risk_distribution": risk_counts,
        "average_risk_score": round(total_score / max(len(unique_accounts), 1), 1),
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.post("/simulate")
def simulate_transaction(txn: TransactionSimulation):
    """
    Simulate scoring for a hypothetical transaction.
    Returns risk assessment for both sender and receiver.
    """
    start = time.time()
    txns, accounts, devices, G = _get_data()

    sender_result = score_account(txn.sender, txns=txns, accounts=accounts,
                                   devices=devices, G=G)
    receiver_result = score_account(txn.receiver, txns=txns, accounts=accounts,
                                     devices=devices, G=G)

    # Decision logic
    max_risk = max(sender_result["risk_score"], receiver_result["risk_score"])
    if max_risk >= 70:
        decision = "BLOCK"
        reason = "High mule risk detected"
    elif max_risk >= 40:
        decision = "FLAG"
        reason = "Suspicious pattern — requires monitoring"
    else:
        decision = "ALLOW"
        reason = "Normal risk profile"

    return {
        "transaction": {
            "sender": txn.sender,
            "receiver": txn.receiver,
            "amount": txn.amount,
        },
        "decision": decision,
        "decision_reason": reason,
        "sender_risk": sender_result,
        "receiver_risk": receiver_result,
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }
