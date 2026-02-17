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


# ── Dashboard API (for React frontend) ───────────────────────────────

def _get_dashboard_data():
    """Compute and cache all pre-scored dashboard data."""
    if "dashboard" not in _cache:
        txns, accounts, devices, G = _get_data()
        unique_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
        all_scores = batch_score_accounts(unique_accounts, txns, accounts, devices, G)

        scores_list = []
        for acc in unique_accounts:
            r = all_scores[acc]
            scores_list.append({
                "account": acc,
                "risk_score": int(r["risk_score"]),
                "risk_level": r["risk_level"],
                "confidence": r.get("confidence", "N/A"),
                "recommended_action": r.get("recommended_action", ""),
                "behavioral_score": int(r.get("behavioral_score", 0)),
                "graph_score": int(r.get("graph_score", 0)),
                "device_score": int(r.get("device_score", 0)),
                "temporal_score": int(r.get("temporal_score", 0)),
                "ml_anomaly_score": round(float(r.get("ml_anomaly_score", 0)), 1),
                "ml_anomaly_label": r.get("ml_anomaly_label", "N/A"),
                "signal_count": int(r.get("signal_count", 0)),
                "reasons": r.get("reasons", []),
                "top_reason": r["reasons"][0] if r.get("reasons") else "No flags",
            })

        scores_list.sort(key=lambda x: x["risk_score"], reverse=True)
        risk_scores = [s["risk_score"] for s in scores_list]

        _cache["dashboard"] = {
            "scores": scores_list,
            "unique_accounts": unique_accounts,
            "summary": {
                "total_accounts": len(unique_accounts),
                "total_transactions": len(txns),
                "critical_count": sum(1 for s in scores_list if s["risk_level"] == "CRITICAL"),
                "high_count": sum(1 for s in scores_list if s["risk_level"] == "HIGH"),
                "medium_count": sum(1 for s in scores_list if s["risk_level"] == "MEDIUM"),
                "low_count": sum(1 for s in scores_list if s["risk_level"] == "LOW"),
                "avg_score": round(sum(risk_scores) / max(len(risk_scores), 1), 1),
                "max_score": max(risk_scores) if risk_scores else 0,
                "median_score": int(sorted(risk_scores)[len(risk_scores) // 2]) if risk_scores else 0,
                "graph_nodes": G.number_of_nodes(),
                "graph_edges": G.number_of_edges(),
            },
        }
    return _cache["dashboard"]


@app.get("/api/dashboard")
def dashboard():
    """Return all pre-computed scores and summary for the React dashboard."""
    return _get_dashboard_data()


@app.get("/api/network")
def network(max_nodes: int = Query(80), risk_filter: str = Query("all")):
    """Return graph nodes and edges for vis-network rendering."""
    txns_df, _, _, _ = _get_data()
    data = _get_dashboard_data()
    scores_map = {s["account"]: s for s in data["scores"]}
    unique = data["unique_accounts"]

    filters = {
        "critical": lambda a: scores_map.get(a, {}).get("risk_level") == "CRITICAL",
        "critical_high": lambda a: scores_map.get(a, {}).get("risk_level") in ("CRITICAL", "HIGH"),
        "high_medium": lambda a: scores_map.get(a, {}).get("risk_level") in ("CRITICAL", "HIGH", "MEDIUM"),
    }

    if risk_filter in filters:
        visible = [a for a in unique if filters[risk_filter](a)][:max_nodes]
    else:
        visible = sorted(unique, key=lambda a: scores_map.get(a, {}).get("risk_score", 0), reverse=True)[:max_nodes]

    visible_set = set(visible)
    color_map = {"CRITICAL": "#ff1744", "HIGH": "#ff5722", "MEDIUM": "#ff9800", "LOW": "#4caf50"}
    size_map = {"CRITICAL": 45, "HIGH": 35, "MEDIUM": 22, "LOW": 12}

    nodes = []
    for acc in visible_set:
        r = scores_map.get(acc, {})
        lvl = r.get("risk_level", "LOW")
        nodes.append({
            "id": acc,
            "label": acc.split("@")[0],
            "color": color_map.get(lvl, "#555"),
            "size": size_map.get(lvl, 15),
            "title": f"{acc}\nScore: {r.get('risk_score', 0)}/100\nLevel: {lvl}\nBehavioral: {r.get('behavioral_score', 0)} | Graph: {r.get('graph_score', 0)} | Device: {r.get('device_score', 0)}",
        })

    edges = []
    for _, row in txns_df.iterrows():
        s, recv = str(row["sender"]), str(row["receiver"])
        if s in visible_set and recv in visible_set:
            edges.append({
                "from": s, "to": recv,
                "value": float(row["amount"]),
                "title": f"\u20b9{float(row['amount']):,.0f}",
            })

    return {"nodes": nodes, "edges": edges}


@app.get("/api/timeline")
def timeline():
    """Return transaction timeline data for temporal analysis charts."""
    txns_df, _, _, _ = _get_data()
    data = _get_dashboard_data()
    scores_map = {s["account"]: s for s in data["scores"]}

    if "timestamp" not in txns_df.columns:
        return {"error": "No timestamp data available"}

    tdf = txns_df.copy()
    tdf["timestamp"] = pd.to_datetime(tdf["timestamp"], errors="coerce")
    tdf = tdf.dropna(subset=["timestamp"])

    transactions = [{
        "timestamp": row["timestamp"].isoformat(),
        "sender": str(row["sender"]),
        "receiver": str(row["receiver"]),
        "amount": float(row["amount"]),
        "sender_risk": scores_map.get(str(row["sender"]), {}).get("risk_level", "UNKNOWN"),
    } for _, row in tdf.iterrows()]

    tdf["hour"] = tdf["timestamp"].dt.floor("h")
    hourly_agg = tdf.groupby("hour").agg(
        count=("amount", "count"), volume=("amount", "sum")
    ).reset_index()
    hourly = [{
        "hour": str(r["hour"]), "count": int(r["count"]), "volume": float(r["volume"])
    } for _, r in hourly_agg.iterrows()]

    tdf["hour_of_day"] = tdf["timestamp"].dt.hour
    tdf["day_name"] = tdf["timestamp"].dt.day_name()
    pivot = tdf.pivot_table(
        values="amount", index="day_name", columns="hour_of_day",
        aggfunc="count", fill_value=0,
    )
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])

    return {
        "transactions": transactions,
        "hourly": hourly,
        "heatmap": {
            "days": pivot.index.tolist(),
            "hours": [int(h) for h in pivot.columns.tolist()],
            "values": [[int(v) for v in row] for row in pivot.values.tolist()],
        },
    }


@app.get("/api/report")
def report():
    """Generate an investigation report in Markdown."""
    data = _get_dashboard_data()
    s = data["summary"]
    alerts = [sc for sc in data["scores"] if sc["risk_level"] in ("CRITICAL", "HIGH")]
    total = s["total_accounts"]

    md = f"""# UPI MULE DETECTION \u2014 INVESTIGATION REPORT
**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
**System:** UPI Mule Detection Platform v2.0

---

## Executive Summary
- **Accounts Analyzed:** {total}
- **Transactions Processed:** {s['total_transactions']}
- **Average Risk Score:** {s['avg_score']}/100

## Risk Distribution
| Level | Count | Percentage |
|-------|-------|------------|
| CRITICAL | {s['critical_count']} | {s['critical_count']/max(total,1)*100:.1f}% |
| HIGH | {s['high_count']} | {s['high_count']/max(total,1)*100:.1f}% |
| MEDIUM | {s['medium_count']} | {s['medium_count']/max(total,1)*100:.1f}% |
| LOW | {s['low_count']} | {s['low_count']/max(total,1)*100:.1f}% |

## Detection Methodology
Five independent detection signals (ensemble approach):
1. **Behavioral Analysis (25%)** \u2014 Velocity, flow asymmetry, amount anomalies
2. **Graph Analytics (40%)** \u2014 Star patterns, chains, circular networks
3. **Device Correlation (15%)** \u2014 Device sharing, multi-device spoofing
4. **Temporal Analysis (10%)** \u2014 Burst detection, odd-hour activity, bot signatures
5. **ML Anomaly Detection (10%)** \u2014 Isolation Forest + Z-score (unsupervised)

## Flagged Accounts
"""
    for a in alerts:
        md += f"\n### {a['account']}\n"
        md += f"- **Score:** {a['risk_score']}/100 | **Level:** {a['risk_level']} | **Confidence:** {a['confidence']}\n"
        md += f"- **Action:** {a['recommended_action']}\n"
        md += "- **Evidence:**\n"
        for reason in a["reasons"][:5]:
            md += f"  - {reason}\n"

    md += """
---
## Recommendations
1. **CRITICAL accounts:** Immediate freeze, file SAR, alert cyber cell
2. **HIGH risk accounts:** Manual investigation within 24 hours
3. **MEDIUM accounts:** Add to enhanced monitoring watchlist
4. **LOW accounts:** Continue routine monitoring

---
*Auto-generated by UPI Mule Detection Platform \u2014 CSIC 1.0*
"""
    return {"report": md}
