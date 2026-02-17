# UPI Mule Detection — System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "Frontend (React + Vite)"
        UI[8-Tab Dashboard SPA]
        CC[Command Center]
        RA[Risk Analysis + Search]
        ML[ML Insights]
        NG[Network Graph]
        TL[Timeline]
        AL[Alerts Console]
        API_TEST[Real-Time API]
        AB[About / Docs]
        UI --> CC & RA & ML & NG & TL & AL & API_TEST & AB
    end

    subgraph "API Gateway (FastAPI v2.1)"
        MW[Security Middleware]
        RL[Rate Limiter<br>120 req/min/IP]
        AK[API Key Auth<br>X-API-Key Header]
        TM[Telemetry Middleware]
        AL2[Audit Logger<br>JSON Structured Logs]
        MW --> RL --> AK --> TM --> AL2
    end

    subgraph "REST Endpoints"
        E1[GET /score/account_id]
        E2[POST /batch_score]
        E3[POST /simulate]
        E4[GET /stats]
        E5[GET /api/dashboard]
        E6[GET /api/network]
        E7[GET /api/timeline]
        E8[GET /api/report]
        E9[GET /metrics]
        E10[GET /health]
    end

    subgraph "5-Factor Detection Engine"
        BE[Behavioral Analysis<br>25% weight]
        GA[Graph Analytics<br>40% weight]
        DR[Device Risk<br>15% weight]
        TA[Temporal Analysis<br>10% weight]
        MLA[ML Anomaly Detection<br>10% weight]
    end

    subgraph "ML Pipeline"
        FE[Feature Engineering<br>17 features/account]
        IF[Isolation Forest<br>Custom NumPy<br>100 trees]
        ZS[Z-Score Outlier<br>Statistical Detection]
        EN[Ensemble<br>70% IF + 30% ZS]
        MP[Model Persistence<br>Pickle + JSON meta]
        FI[Feature Importance<br>Permutation-based]
        EX[SHAP-like<br>Local Explanations]
        FE --> IF & ZS
        IF --> EN
        ZS --> EN
        IF --> MP
        IF --> FI
        IF --> EX
    end

    subgraph "Risk Aggregation"
        WS[Weighted Score<br>Base = Σ Wi × Si]
        CB[Confidence Boosting<br>+8 to +20 multi-signal]
        RL2[Risk Classification<br>CRITICAL/HIGH/MED/LOW]
        EV[Evidence Generation<br>3-5 explainable items]
        WS --> CB --> RL2 --> EV
    end

    subgraph "Data Layer"
        TX[(transactions.csv)]
        AC[(accounts.csv)]
        DV[(devices.csv)]
        GR[NetworkX Graph<br>In-Memory Cache]
        TX & AC & DV --> GR
    end

    subgraph "Infrastructure"
        DC[Docker Container<br>python:3.11-slim]
        DCO[docker-compose<br>Multi-service]
        LOG[Audit Logs<br>logs/audit.log]
        MOD[Model Store<br>models/]
    end

    UI -->|HTTP/REST| MW
    MW --> E1 & E2 & E3 & E4 & E5 & E6 & E7 & E8 & E9 & E10
    E1 & E2 --> BE & GA & DR & TA & MLA
    MLA --> FE
    BE & GA & DR & TA & MLA --> WS
```

## Data Flow — Single Account Scoring

```mermaid
sequenceDiagram
    participant U as User/Frontend
    participant MW as Middleware
    participant API as /score/{id}
    participant B as Behavioral
    participant G as Graph
    participant D as Device
    participant T as Temporal
    participant ML as ML Engine
    participant RE as Risk Engine

    U->>MW: GET /score/acc123
    MW->>MW: Rate limit check
    MW->>MW: API key validation
    MW->>API: Forward request
    
    par Parallel Analysis
        API->>B: behavior_risk(txns, meta)
        API->>G: graph_risk(id, G)
        API->>D: device_risk(id, devices)
        API->>T: temporal_risk(id, txns)
        API->>ML: ml_anomaly(id, cache)
    end
    
    B-->>API: score=45, reasons[]
    G-->>API: score=60, reasons[]
    D-->>API: score=20, reasons[]
    T-->>API: score=30, reasons[]
    ML-->>API: score=72, label=ANOMALOUS
    
    API->>RE: aggregate(45,60,20,30,72)
    RE->>RE: Base = 0.25×45 + 0.40×60 + ...
    RE->>RE: Boost = +15 (3 signals aligned)
    RE-->>API: score=68, level=MEDIUM
    
    API-->>MW: Response + telemetry
    MW->>MW: Audit log entry
    MW-->>U: JSON response (< 200ms)
```

## Security Architecture

```mermaid
graph LR
    subgraph "Security Layers"
        A[CORS<br>Whitelisted Origins]
        B[Rate Limiting<br>120 req/min/IP]
        C[API Key Auth<br>X-API-Key Header]
        D[Input Validation<br>Pydantic Models]
        E[Audit Logging<br>Every Request]
        F[Non-root Container<br>Docker Security]
    end
    A --> B --> C --> D --> E --> F
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite | SPA Dashboard |
| **Visualization** | Plotly.js, vis-network | Charts & Graph |
| **Backend** | FastAPI (Python 3.11) | REST API |
| **ML Engine** | Custom Isolation Forest (NumPy) | Anomaly Detection |
| **Graph** | NetworkX | Transaction Network Analysis |
| **Data** | Pandas + CSV | Data Processing |
| **Containerization** | Docker + Compose | Deployment |
| **Logging** | Structured JSON logs | Audit Trail |
