
# FinGuard - UPI Mule Account Detection System

This project is a prototype platform to detect mule accounts in UPI (Unified Payments Interface) transactions. It combines rule-based, graph-based, device-based, temporal, and machine learning analysis to flag suspicious accounts. The system includes a backend API, a modern dashboard, and tools for data generation and testing.

---

## What It Does

- Analyzes UPI transaction data to find accounts that may be used for money laundering or fraud ("mule accounts").
- Uses multiple signals: behavior, transaction network patterns, device usage, timing, and ML-based anomaly detection.
- Provides a web dashboard for real-time monitoring, investigation, and reporting.

---

## Main Features

- **5-factor risk scoring:**
    - Behavioral: unusual activity, new accounts, pass-through, spikes
    - Graph: star, chain, circular, relay, distributor patterns
    - Device: shared or spoofed devices
    - Temporal: bursts, odd hours, bot-like timing
    - ML anomaly: Isolation Forest (custom NumPy), Z-score
- **Dashboard:**
    - Tabs for command center, risk analysis, ML insights, network graph, timeline, alerts, API testing, and documentation
- **API:**
    - FastAPI backend with endpoints for scoring, simulation, stats, and more
- **Security:**
    - API-key, rate limiting, CORS, audit logging, non-root Docker
- **Customizable:**
    - Change risk weights, thresholds, and add new detection patterns easily

---


## How to Run

### Local

1. Create a Python virtual environment and activate it
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Start backend:
    ```bash
    uvicorn backend.app:app --reload
    ```
4. To run the React frontend (recommended for most users):
    ```bash
    cd frontend
    npm install
    npm run dev
    ```
    - Open http://localhost:3000

---

## Dashboard Overview

- **Command Center:** Key metrics and risk heatmap
- **Risk Analysis:** Search, filter, and investigate flagged accounts
- **ML Insights:** Visualize anomaly scores
- **Network Graph:** Explore transaction patterns
- **Timeline:** See activity over time
- **Real-Time API:** Test API endpoints live
- **About:** Documentation and system info

---

## How Detection Works

1. **Behavioral:** Flags new, fast, or high-volume accounts
2. **Graph:** Finds suspicious network patterns (e.g., many inflows to one outflow)
3. **Device:** Detects shared or spoofed devices
4. **Temporal:** Looks for bursts, odd hours, or bot-like timing
5. **ML Anomaly:** Uses unsupervised ML to spot outliers

All signals are combined into a final risk score. Accounts are labeled as LOW, MEDIUM, HIGH, or CRITICAL risk, with recommended actions.

---

## API Endpoints (Backend)

- `GET /health` – Health check
- `GET /score/{account_id}` – Score a single account
- `POST /batch_score` – Score multiple accounts
- `POST /simulate` – Simulate a transaction
- `GET /api/dashboard` – Dashboard data
- `GET /api/network` – Network graph data
- `GET /api/timeline` – Timeline data
- `GET /api/report` – Investigation report
- `GET /metrics` – Performance metrics

See http://localhost:8000/docs for full API documentation.

---

## Project Structure

```
UPI_Mule_Account_Detection/
├── backend/      # FastAPI backend and risk logic
├── frontend/     # React dashboard
├── data/         # Sample data (transactions, accounts, devices)
├── models/       # ML model files
├── logs/         # Audit logs
├── scripts/      # Data generators
├── docs/         # Architecture and demo docs
├── Dockerfile    # Production container
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Customization

- Change risk thresholds and weights in `backend/core/risk_engine.py`
- Add new detection logic in `backend/core/`
- Tune ML model in `backend/core/ml_anomaly.py`
- Add new test scenarios in `scripts/enhanced_data_generator.py`

---

## Testing

Run backend and system tests:
```bash
python test_backend.py
python test_system.py
```

---

## Security & Compliance

- API-key authentication (X-API-Key header)
- Rate limiting (120 req/min per IP)
- CORS whitelisting
- Structured audit logging
- Input validation (Pydantic)
- Non-root Docker container
- Request tracing (X-Request-Id)

---



## Dashboard Walkthrough

| Tab | Purpose |
|-----|---------|
| **Command Center** | Overview metrics, risk distribution, component analysis |
| **Risk Analysis** | Filter, sort, drill-down into individual accounts with evidence |
| **ML Insights** | Isolation Forest & Z-score anomaly visualization |
| **Network Graph** | Interactive transaction graph with risk-based coloring |
| **Timeline** | Temporal analysis of transaction patterns |
| **Real-Time API** | Live API testing and transaction simulation |
| **About** | Algorithm explanation, scoring formula, architecture |

---

## Detection Algorithm

### Five Independent Risk Signals

**Behavioral (25%)**
- Velocity spikes (5-10+ transactions: +25-35 pts)
- New account rapid activity (0-7 days = +40 pts, 0-30 days = +30 pts)
- Pass-through ratio (80-120% inflow→outflow = +35 pts)
- Amount anomalies (avg > ₹5K = +20 pts, max > ₹10K = +15 pts)
- Total volume spike (> ₹50K = +20 pts)
- Pure sender pattern (no receiving txns = +20 pts)

**Graph Analysis (40%)** [STRONGEST SIGNAL]
- Star patterns: 3-5+ inflows → 1 outflow (+30-45 pts)
- Distributors: 1 inflow → 3-5+ outflows (+30-45 pts)
- Relay nodes: High in/out degree processing (+35 pts)
- Chains: Linear laundering paths A→B→C→D (+20-35 pts)
- Circular: Fund rotation loops A→B→C→A (+50 pts)

**Device (15%)**
- Device shared across 3-10+ accounts (+30-50 pts)
- Multi-device control / spoofing (+20-30 pts)

**Temporal (10%)**
- Rapid-fire bursts (< 60s between txns = +35 pts)
- Odd-hour activity (12AM-5AM concentration = +15-30 pts)
- Velocity spikes (3x+ rate increase = +25 pts)
- Weekend concentration (> 70% on weekends = +15 pts)
- Uniform timing / bot signature (low CV = +20-30 pts)

**ML Anomaly (10%)**
- Isolation Forest (unsupervised, pure NumPy implementation)
- Z-score statistical outlier detection
- Ensemble: 70% IF + 30% Z-score
- Labels: ANOMALOUS (70+), SUSPICIOUS (45-69), NORMAL (<45)

### Final Score
```
Base = (0.25 × Behavioral) + (0.40 × Graph) + (0.15 × Device)
     + (0.10 × Temporal) + (0.10 × ML Anomaly)

Boost: +8 (2 signals) / +15 (3 signals) / +20 (4+ signals)
       +10 (graph & device correlated) / +8 (behavioral & graph)
       +12 (extreme triple correlation)

Score = min(Base + Boost, 100)
```

### Risk Levels
- **CRITICAL (85+):** Block immediately — freeze account, alert compliance, file SAR
- **HIGH (70-84):** Investigate — manual review within 24h, enhanced monitoring
- **MEDIUM (40-69):** Monitor — add to watchlist, periodic review
- **LOW (<40):** Allow — normal operations, routine monitoring

---

## Test Scenarios (Built-in)

Your test data includes these known mule accounts:

| Account | Pattern | Expected Risk |
|---------|---------|---------------|
| `mule_aggregator@upi` | Star aggregator (5→1), burst timing | CRITICAL/HIGH |
| `circle_node_*@upi` | Circular loop (A→B→C→D→A) | CRITICAL/HIGH |
| `chain_node_*@upi` | Laundering chain | MEDIUM-HIGH |
| `device_ring_*@upi` | Same device on 3 accounts | HIGH |
| `new_mule_account@upi` | 1-day-old + rapid burst txns | HIGH |

---

## Project Structure

```
MVP/
├── backend/
│   ├── app.py                       # FastAPI v2.1.0 (11 endpoints, security middleware)
│   ├── api/
│   │   └── score.py                 # Single & batch scoring logic
│   ├── core/
│   │   ├── behavioral.py            # Velocity, pass-through, new-account detection
│   │   ├── graph_analysis.py        # Network patterns (star, chain, circular, relay)
│   │   ├── device_risk.py           # Device concentration & multi-device scoring
│   │   ├── temporal_analysis.py     # Time-based anomaly detection (bursts, bots)
│   │   ├── ml_anomaly.py            # Isolation Forest + Z-score + persistence + SHAP
│   │   └── risk_engine.py           # 5-factor aggregation & confidence boost
│   └── utils/
│       ├── data_loader.py           # CSV data loaders
│       └── helpers.py               # Timestamp utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx                  # 8-tab SPA with sidebar
│   │   ├── api.js                   # API client (all endpoints)
│   │   └── components/              # React components (8 tabs)
│   ├── package.json                 # Frontend dependencies
│   └── vite.config.js               # Vite config with proxy
├── data/
│   ├── transactions.csv             # Simulated UPI transactions with timestamps
│   ├── accounts.csv                 # Account metadata (age, type)
│   └── devices.csv                  # Device-account mappings
├── models/                          # ML model persistence (auto-generated)
│   ├── isolation_forest.pkl         # Trained Isolation Forest model
│   └── model_meta.json              # Training metadata
├── logs/
│   └── audit.log                    # Structured JSON audit logs (auto-generated)
├── scripts/
│   ├── data_generator.py            # Basic data generator
│   └── enhanced_data_generator.py   # 5-scenario mule data generator
├── docs/
│   ├── architecture.md              # System architecture diagrams (Mermaid)
│   └── demo_flow.md                 # Demo walkthrough for judges
├── Dockerfile                       # Production container (non-root, health-checked)
├── docker-compose.yml               # Multi-service orchestration
├── .dockerignore                    # Docker build exclusions
├── test_backend.py                  # Backend scoring tests
├── test_system.py                   # System integration tests
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Backend API (For Integration)

Start server:
```bash
python -m uvicorn backend.app:app --reload
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info & available endpoints |
| GET | `/health` | Health check with data statistics |
| GET | `/score/{account_id}` | Score a single account |
| POST | `/batch_score` | Score multiple accounts in one call |
| GET | `/stats` | System-wide risk distribution |
| POST | `/simulate` | Simulate a transaction & get risk decision |
| GET | `/api/dashboard` | Pre-computed dashboard data |
| GET | `/api/network` | Graph nodes/edges for vis-network |
| GET | `/api/timeline` | Transaction timeline + heatmap |
| GET | `/api/report` | Auto-generated investigation report |
| GET | `/metrics` | Performance & operational telemetry |

### Example: Score Endpoint

```
GET http://127.0.0.1:8000/score/{account_id}
```

Response:
```json
{
  "account_id": "mule_aggregator@upi",
  "risk_score": 95,
  "risk_level": "CRITICAL",
  "confidence": "VERY HIGH",
  "recommended_action": "BLOCK IMMEDIATELY - Freeze account, alert compliance, file SAR",
  "behavioral_score": 100,
  "graph_score": 85,
  "device_score": 60,
  "temporal_score": 35,
  "ml_anomaly_score": 72.5,
  "ml_anomaly_label": "ANOMALOUS",
  "signal_count": 4,
  "reasons": [
    "Star-pattern mule behavior (5 inflows → 1 outflow)",
    "Mule indicator: 95% of inflow sent back out",
    "High transaction velocity (10 txns)",
    "Rapid-fire burst: 4 transactions within 60 seconds (bot-like)"
  ],
  "response_time_ms": 45.2,
  "timestamp": "2026-02-12T10:30:00"
}
```

### Example: Simulate Transaction

```
POST http://127.0.0.1:8000/simulate
Body: {"sender": "user_1@upi", "receiver": "mule_aggregator@upi", "amount": 5000}
```

Returns risk assessment for both parties with a decision: **BLOCK**, **FLAG**, or **ALLOW**.

API docs available at: **http://127.0.0.1:8000/docs** (Swagger UI) and **/redoc** (ReDoc).

---

## Testing

```bash
# Backend unit tests
python test_backend.py

# System integration tests
python test_system.py
```

Output shows all CRITICAL/HIGH risk accounts detected with evidence and signal counts.

---

## Performance

- **Full analysis:** < 2 seconds for 50+ accounts
- **Batch scoring:** One-pass graph cycle detection + batch ML inference
- **ML inference:** Lightweight Isolation Forest (pure NumPy, no sklearn needed)
- **Memory:** Efficient O(n) storage, O(V·depth) graph algorithms
- **Scalability:** Architecture scales linearly with account count

---

## Customization

### Adjust Risk Thresholds
Edit `backend/core/risk_engine.py`:
```python
def risk_level(score):
    if score >= 85:      # CRITICAL threshold
        return "CRITICAL"
    elif score >= 70:    # HIGH threshold
        return "HIGH"
    elif score >= 40:    # MEDIUM threshold
        return "MEDIUM"
    return "LOW"
```

### Change Weight Distribution
Edit `backend/core/risk_engine.py`:
```python
base_score = (
    0.25 * behavioral   # Adjust weights (must sum to 1.0)
    + 0.40 * graph
    + 0.15 * device
    + 0.10 * temporal
    + 0.10 * ml_anomaly
)
```

### Tune ML Anomaly Detection
Edit `backend/core/ml_anomaly.py`:
```python
iforest = IsolationForestLite(
    n_trees=100,        # More trees = more stable (slower)
    max_samples=256,    # Subsample size per tree
)
# Ensemble weighting
ensemble_scores = 0.7 * anomaly_scores + 0.3 * z_normalized
```


## What Works

Circular mule network detection (CRITICAL risk)  
Star aggregator pattern (CRITICAL/HIGH risk)  
Chain laundering paths (MEDIUM-HIGH detection)  
New account rapid onboarding (HIGH risk)  
Device-based fraud rings (HIGH risk)  
Temporal burst & bot detection  
ML-based unsupervised anomaly flagging  
Real-time transaction simulation with BLOCK/FLAG/ALLOW  
Interactive network visualization  
Detailed forensic drill-down  
Auto-generated investigation reports  


---

## Security & Compliance

| Layer | Implementation | Status |
|-------|---------------|--------|
| **Authentication** | API-key via `X-API-Key` header | Implemented |
| **Rate Limiting** | 120 req/min per IP (in-memory) | Implemented |
| **CORS** | Whitelisted origins only | Hardened |
| **Audit Logging** | Structured JSON (`logs/audit.log`) | Implemented |
| **Input Validation** | Pydantic schemas on all endpoints | Implemented |
| **Container Security** | Non-root user, minimal base image | Implemented |
| **Request Tracing** | `X-Request-Id` on every response | Implemented |
| **Secrets Management** | Environment variables (`MULE_API_KEY`) | Configurable |

---

## Scalability & Deployment Roadmap

| Phase | Capability | Status |
|-------|-----------|--------|
| **MVP (Current)** | Docker + Compose, health checks, hot reload | Done |
| **Pilot** | Kubernetes manifests, Redis rate limiting, PostgreSQL |  Planned |
| **Scale** | Kafka stream ingestion, real-time WebSocket, horizontal autoscaling |  Planned |
| **Enterprise** | SSO/OAuth2, RBAC, multi-tenant isolation, SLA monitoring | Planned |


---

## Support

**For demo/questions:**
1. Run `python test_backend.py` to verify detection works
2. Check the **About** tab in dashboard for algorithm explanation
3. Review account evidence in **Risk Analysis** tab for debugging
4. Use **Real-Time API** tab to test live scoring
5. Read DEPLOYMENT_GUIDE.md for troubleshooting

---

