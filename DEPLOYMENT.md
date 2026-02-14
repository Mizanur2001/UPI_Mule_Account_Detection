# Deployment Guide

## Quick Start (5 minutes)

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (optional)

### Option 1: Local Development (Recommended for Demo)

```bash
# Terminal 1: Backend
cd UPI_Mule_Account_Detection
python -m uvicorn backend.app:app --port 8000 --reload

# Terminal 2: Frontend
cd UPI_Mule_Account_Detection/frontend
npm install
npm run dev

# Open: http://localhost:3000
```

### Option 2: Docker (Production-Ready)

```bash
cd UPI_Mule_Account_Detection
docker-compose up --build

# Open: http://localhost:3000
```

---

## Configuration

### Backend Environment

Set in `backend/.env` or system env:

```env
# API Port
PORT=8000

# Logging
LOG_LEVEL=INFO

# CORS Origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173

# JWT Secret (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
JWT_SECRET_KEY=your-secret-key-here

# Data
DATA_PATH=backend/data
```

### Frontend Environment

File: `frontend/.env`

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_WEBSOCKET=false
```

---

## Production Deployment

### Docker Compose Stack

```yaml
# Services
- Backend API (port 8000)
- Frontend UI (port 3000)
- Health checks every 30 seconds
- Auto-restart on failure
- Network isolation
```

### Deployment Steps

1. **Build Images**
   ```bash
   docker-compose build --no-cache
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Verify Health**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

4. **View Logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

5. **Stop Services**
   ```bash
   docker-compose down
   ```

---

## Data Setup

### CSV Files Location

```
backend/data/
├── accounts.csv       # Account metadata
├── transactions.csv   # Transaction history
└── devices.csv        # Device information
```

### CSV Format

**transactions.csv**
```
sender,receiver,amount,timestamp,channel
ACC001,ACC002,5000,2024-01-01T10:00:00,UPI
```

**accounts.csv**
```
account_id,account_holder_type,account_age_days
ACC001,Individual,365
```

**devices.csv**
```
device_id,device_type,last_seen
DEV001,Mobile,2024-01-01T10:00:00
```

---

## Health Checks

### API Health

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-02-14T18:00:38",
  "data": {
    "transactions": 306,
    "accounts": 174,
    "devices": 174,
    "graph_nodes": 174,
    "graph_edges": 260
  }
}
```

### API Documentation

Open: **http://localhost:8000/docs** (interactive Swagger UI)

---

## Troubleshooting

### Backend Won't Start

```
Error: ModuleNotFoundError: No module named 'backend'
```

**Fix**: Run from project root, not backend folder
```bash
cd UPI_Mule_Account_Detection  # ← Root folder
python -m uvicorn backend.app:app --port 8000
```

### Frontend Shows "No Data"

```
Error: "Failed to connect to backend"
```

**Fix**: Check backend is running on port 8000
```bash
curl http://localhost:8000/health
```

### Port Already in Use

```
Error: Address already in use
```

**Fix**: Kill existing processes
```bash
# Kill all Python processes
Get-Process python | Stop-Process -Force

# Kill all Node processes
Get-Process node | Stop-Process -Force
```

### Database Files Not Found

```
Error: Transactions file not found: data/transactions.csv
```

**Fix**: Ensure CSV files are in `backend/data/`:
```bash
C:\Users\suvom\OneDrive\Desktop\ICRH\FinalS\UPI_Mule_Account_Detection\backend\data\
```

---

## Performance Tuning

### For High Load

1. **Increase Workers** (backend)
   ```bash
   python -m uvicorn backend.app:app --workers 4 --port 8000
   ```

2. **Enable Caching**
   ```python
   # Already enabled in code (5-minute TTL)
   ```

3. **Add Load Balancer**
   ```bash
   # Use nginx or HAProxy in front of Docker containers
   ```

### For Large Datasets

1. **Upgrade to PostgreSQL**
   ```bash
   # Update data_loader.py to connect to PostgreSQL
   ```

2. **Add Redis**
   ```bash
   # Cache frequently accessed data
   ```

---

## Monitoring

### Logs

```bash
# Backend logs
docker-compose logs -f backend

# Frontend logs
docker-compose logs -f frontend

# All services
docker-compose logs -f
```

### Resource Usage

```bash
docker stats
```

---

## Security Checklist

Before production:

- [ ] Change JWT_SECRET_KEY
- [ ] Set LOG_LEVEL=WARNING
- [ ] Enable HTTPS (nginx reverse proxy)
- [ ] Rotate credentials regularly
- [ ] Enable firewall rules
- [ ] Monitor for suspicious activity
- [ ] Back up data regularly
- [ ] Test disaster recovery

---

## Support

For issues:
1. Check logs: `docker-compose logs backend`
2. Visit API docs: http://localhost:8000/docs
3. Test endpoints with curl or Postman
4. Review ARCHITECTURE.md for design details
