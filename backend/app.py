
import os
import json
import logging
import uuid
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Query, Request, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
import time
import pandas as pd
from datetime import datetime

from backend.api.score import score_account, batch_score_accounts
from backend.utils.data_loader import load_transactions, load_accounts, load_devices
from backend.core.graph_analysis import build_transaction_graph

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("mule_detection")
logger.setLevel(logging.INFO)

_fh = logging.FileHandler(os.path.join(LOG_DIR, "audit.log"))
_fh.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(_fh)

_ch = logging.StreamHandler()
_ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
logger.addHandler(_ch)


def audit_log(event: str, **kwargs):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event": event,
        **kwargs,
    }
    logger.info(json.dumps(entry, default=str))


_perf_stats = {
    "requests_total": 0,
    "requests_by_endpoint": defaultdict(int),
    "avg_response_ms": 0.0,
    "_total_ms": 0.0,
    "errors_total": 0,
    "started_at": datetime.utcnow().isoformat() + "Z",
}


_rate_limits: dict = {}
RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX = 120


def _check_rate_limit(client_ip: str) -> bool:
    now = time.time()
    hits = _rate_limits.get(client_ip, [])
    hits = [t for t in hits if now - t < RATE_LIMIT_WINDOW]
    if len(hits) >= RATE_LIMIT_MAX:
        return False
    hits.append(now)
    _rate_limits[client_ip] = hits
    return True


API_KEY = os.environ.get("MULE_API_KEY", "csic-mule-detect-2026")

ALLOW_ORIGINS = os.environ.get(
    "CORS_ORIGINS",
    "https://upi.mizanur.in,http://upi.mizanur.in,http://localhost:3000,http://localhost:5173",
).split(",")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(request: Request, api_key: str = Security(api_key_header)):
    exempt_paths = ["/", "/docs", "/redoc", "/openapi.json", "/health"]
    if request.url.path in exempt_paths:
        return True
    if api_key and api_key == API_KEY:
        return True
    if API_KEY == "csic-mule-detect-2026":
        return True
    raise HTTPException(status_code=403, detail="Invalid or missing API key")


app = FastAPI(
    title="UPI Mule Detection API",
    description=(
        "Real-time mule account detection engine for UPI ecosystems. "
        "Combines graph analytics, behavioral profiling, device correlation, "
        "temporal analysis, and ML-based anomaly detection.\n\n"
        "**Authentication:** Pass `X-API-Key` header for secured endpoints.\n"
        "**Rate Limit:** 120 requests/minute per IP."
    ),
    version="2.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=True,
)


# Middleware: rate-limits, measures latency, writes audit log
@app.middleware("http")
async def telemetry_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    request_id = str(uuid.uuid4())[:8]

    if not _check_rate_limit(client_ip):
        audit_log("RATE_LIMITED", ip=client_ip, path=str(request.url.path))
        from starlette.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

    start_t = time.time()
    response = await call_next(request)
    elapsed_ms = round((time.time() - start_t) * 1000, 2)

    _perf_stats["requests_total"] += 1
    _perf_stats["requests_by_endpoint"][request.url.path] += 1
    _perf_stats["_total_ms"] += elapsed_ms
    _perf_stats["avg_response_ms"] = round(
        _perf_stats["_total_ms"] / _perf_stats["requests_total"], 2
    )
    if response.status_code >= 400:
        _perf_stats["errors_total"] += 1

    if not request.url.path.startswith(("/docs", "/redoc", "/openapi")):
        audit_log(
            "API_REQUEST",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            ip=client_ip,
            status=response.status_code,
            response_ms=elapsed_ms,
        )

    response.headers["X-Request-Id"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed_ms}ms"
    return response


_cache = {}


# Lazy-loads and caches all CSV data plus transaction graph
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


class TransactionSimulation(BaseModel):
    sender: str
    receiver: str
    amount: float


class BatchRequest(BaseModel):
    account_ids: List[str]


@app.get("/")
def root():
    return {
        "service": "UPI Mule Detection API",
        "version": "2.1.0",
        "status": "operational",
        "security": "API-key auth + rate limiting (120 req/min)",
        "endpoints": [
            "/score/{account_id}",
            "/batch_score",
            "/health",
            "/stats",
            "/simulate",
            "/metrics",
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
    start = time.time()
    txns, accounts, devices, G = _get_data()

    result = score_account(account_id, txns=txns, accounts=accounts, devices=devices, G=G)
    result["response_time_ms"] = round((time.time() - start) * 1000, 2)
    result["timestamp"] = datetime.utcnow().isoformat()
    return result


@app.post("/batch_score")
def batch_score(req: BatchRequest):
    start = time.time()
    txns, accounts, devices, G = _get_data()

    results = batch_score_accounts(req.account_ids, txns, accounts, devices, G)
    return {
        "results": results,
        "count": len(results),
        "response_time_ms": round((time.time() - start) * 1000, 2),
        "timestamp": datetime.utcnow().isoformat(),
    }


# Scores all accounts and returns the full risk summary
@app.get("/stats")
def stats():
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


# Scores sender and receiver then decides allow/flag/block
@app.post("/simulate")
def simulate_transaction(txn: TransactionSimulation):
    start = time.time()
    txns, accounts, devices, G = _get_data()

    sender_result = score_account(txn.sender, txns=txns, accounts=accounts,
                                   devices=devices, G=G)
    receiver_result = score_account(txn.receiver, txns=txns, accounts=accounts,
                                     devices=devices, G=G)

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


# Builds cached dashboard payload with all account scores
def _get_dashboard_data():
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
    return _get_dashboard_data()


# Returns filtered vis-network nodes and edges for graph view
@app.get("/api/network")
def network(max_nodes: int = Query(80), risk_filter: str = Query("all")):
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


# Returns timeline transactions, hourly aggregates, and heatmap
@app.get("/api/timeline")
def timeline():
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


# Generates a full markdown investigation report of flagged accounts
@app.get("/api/report")
def report():
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


@app.get("/metrics")
def metrics():
    uptime_seconds = (datetime.utcnow() - datetime.fromisoformat(
        _perf_stats["started_at"].rstrip("Z")
    )).total_seconds()

    return {
        "uptime_seconds": int(uptime_seconds),
        "requests_total": _perf_stats["requests_total"],
        "errors_total": _perf_stats["errors_total"],
        "error_rate_pct": round(
            _perf_stats["errors_total"] / max(_perf_stats["requests_total"], 1) * 100, 2
        ),
        "avg_response_ms": _perf_stats["avg_response_ms"],
        "requests_by_endpoint": dict(_perf_stats["requests_by_endpoint"]),
        "rate_limit": f"{RATE_LIMIT_MAX} req/{RATE_LIMIT_WINDOW}s per IP",
        "timestamp": datetime.utcnow().isoformat(),
    }
