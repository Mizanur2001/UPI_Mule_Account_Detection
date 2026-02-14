# API Reference

**Base URL**: `http://localhost:8000`  
**API Docs**: `http://localhost:8000/docs` (Interactive Swagger UI)

---

## Endpoints

### 1. Health Check

```
GET /health
```

**Response** (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2026-02-14T18:00:38.779675",
  "data": {
    "transactions": 306,
    "accounts": 174,
    "devices": 174,
    "graph_nodes": 174,
    "graph_edges": 260
  }
}
```

---

### 2. Score Single Account

```
GET /score/{account_id}
```

**Parameters**
- `account_id` (string, required): Account identifier (e.g., "ACC001")

**Response** (200 OK)
```json
{
  "account_id": "ACC001",
  "risk_score": 0.75,
  "risk_level": "HIGH",
  "factors": {
    "behavioral": 0.8,
    "temporal": 0.7,
    "graph": 0.65,
    "device": 0.6,
    "ml_anomaly": 0.85
  },
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

**Risk Levels**
- `CRITICAL`: Score > 0.85 (Likely mule)
- `HIGH`: Score 0.65-0.85 (Suspicious)
- `MEDIUM`: Score 0.40-0.65 (Monitor)
- `LOW`: Score < 0.40 (Safe)

---

### 3. Batch Score Accounts

```
POST /batch_score
Content-Type: application/json
```

**Request Body**
```json
{
  "account_ids": ["ACC001", "ACC002", "ACC003"]
}
```

**Response** (200 OK)
```json
{
  "results": {
    "ACC001": {
      "account_id": "ACC001",
      "risk_score": 0.75,
      "risk_level": "HIGH",
      "factors": {...}
    },
    "ACC002": {...},
    "ACC003": {...}
  },
  "count": 3,
  "response_time_ms": 245.5,
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

---

### 4. Get System Statistics

```
GET /stats
```

**Response** (200 OK)
```json
{
  "total_accounts": 174,
  "total_transactions": 306,
  "risk_distribution": {
    "CRITICAL": 1,
    "HIGH": 16,
    "MEDIUM": 13,
    "LOW": 144
  },
  "average_risk_score": 16.5,
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

---

### 5. Get Transaction Graph

```
GET /transaction_graph
```

**Response** (200 OK)
```json
{
  "nodes": [
    {
      "id": "ACC001",
      "label": "ACC001",
      "risk_score": 0.75,
      "size": 25
    }
  ],
  "edges": [
    {
      "source": "ACC001",
      "target": "ACC002",
      "weight": 5,
      "transactions": 5
    }
  ],
  "cached": false,
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

---

### 6. Login (JWT Token)

```
POST /token
Content-Type: application/x-www-form-urlencoded
```

**Request Body**
```
username=admin&password=admin@123
```

**Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

**Demo Credentials**
```
Username: admin
Password: admin@123

Username: analyst
Password: analyst@456

Username: test
Password: test@789
```

---

### 7. Refresh Token

```
POST /auth/refresh
Authorization: Bearer {refresh_token}
```

**Response** (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 8. Get All Accounts

```
GET /accounts
```

**Response** (200 OK)
```json
{
  "accounts": ["ACC001", "ACC002", "ACC003", ...],
  "count": 174,
  "timestamp": "2026-02-14T18:00:38.779675"
}
```

---

## Authentication

### Bearer Token

Protected endpoints require JWT token in header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Public Endpoints (No Auth Required)

- `GET /health`
- `GET /accounts`
- `GET /score/{id}`
- `POST /batch_score`
- `GET /stats`
- `GET /transaction_graph`

### Protected Endpoints (Auth Required)

- `POST /token` - (special: returns token)
- `POST /auth/refresh`

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid account_id"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 404 Not Found
```json
{
  "detail": "Account not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to score account"
}
```

---

## Rate Limiting

- **Public endpoints**: 100 req/minute
- **Protected endpoints**: 10 req/minute
- **Batch endpoints**: 5 req/minute

---

## Response Times

| Endpoint | Avg Time | Max Time |
|----------|----------|----------|
| `/health` | 10ms | 20ms |
| `/score/{id}` | 158ms | 210ms |
| `/batch_score` (100) | 2.3s | 3.5s |
| `/stats` | 120ms | 180ms |
| `/transaction_graph` | 90ms | 150ms |

---

## Examples

### cURL

```bash
# Score single account
curl http://localhost:8000/score/ACC001

# Batch score
curl -X POST http://localhost:8000/batch_score \
  -H "Content-Type: application/json" \
  -d '{"account_ids": ["ACC001", "ACC002"]}'

# Get stats
curl http://localhost:8000/stats

# Login
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=admin@123"
```

### Python (requests)

```python
import requests

BASE_URL = "http://localhost:8000"

# Score account
response = requests.get(f"{BASE_URL}/score/ACC001")
print(response.json())

# Batch score
response = requests.post(f"{BASE_URL}/batch_score", 
  json={"account_ids": ["ACC001", "ACC002"]})
print(response.json())
```

### JavaScript (fetch)

```javascript
const BASE_URL = "http://localhost:8000";

// Score account
const response = await fetch(`${BASE_URL}/score/ACC001`);
const data = await response.json();
console.log(data);

// Batch score
const response = await fetch(`${BASE_URL}/batch_score`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ account_ids: ["ACC001", "ACC002"] })
});
const data = await response.json();
console.log(data);
```

---

## Pagination

Not implemented (small dataset). Future versions will support:

```
GET /stats?page=1&limit=50
```

---

## Versioning

Current API Version: **v2.0.0**

Future versions will support:
```
GET /v3/score/{id}
```

---

## Support

- **Docs**: http://localhost:8000/docs
- **Schema**: http://localhost:8000/openapi.json
- **Status**: http://localhost:8000/health
