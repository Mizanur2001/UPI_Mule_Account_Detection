# Quick Start Guide

## 🚀 Start Backend (Terminal 1)

```bash
cd UPI_Mule_Account_Detection
python -m uvicorn backend.app:app --port 8000 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify:**
- Open: http://localhost:8000/health
- Should show: ✅ "status": "healthy"

---

## 🚀 Start Frontend (Terminal 2)

```bash
cd UPI_Mule_Account_Detection/frontend
npm install
npm run dev
```

**Expected Output:**
```
VITE v5.4.0 ready in 234 ms
Local: http://localhost:3000/
```

**Verify:**
- Open: http://localhost:3000
- Should show: Dashboard loading data

---

## 🐳 Alternative: Docker (Terminal, Single Command)

```bash
cd UPI_Mule_Account_Detection
docker-compose up --build
```

**Expected Output:**
```
backend service started on port 8000 ✓
frontend service started on port 3000 ✓
```

---

## 📊 Dashboard

Once both services are running:

✅ **Open**: http://localhost:3000

You should see:
- 174 accounts loaded
- 306 transactions recorded
- Risk distribution by level
- Interactive transaction graph

---

## 🔐 API Authentication (Optional)

**Login** to get JWT token:

```bash
curl -X POST http://localhost:8000/token \
  -d "username=admin&password=admin@123"
```

**Response:**
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Demo Credentials:**
```
Username: admin        / Password: admin@123
Username: analyst      / Password: analyst@456
Username: test         / Password: test@789
```

---

## 📚 API Documentation

Open: **http://localhost:8000/docs**

Interactive Swagger UI with all 8 endpoints pre-loaded:
- Test `/score/{account_id}`
- Test `/batch_score`
- Test `/stats`
- Test `/transaction_graph`
- And more...

---

## ✅ Test Everything

```bash
cd backend
pytest tests -v
```

**Expected**: 9/9 tests PASSED ✅

---

## 🛑 Stop Services

**Ctrl+C** in both terminals

or

```bash
docker-compose down
```

---

## ❌ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port 3000 already in use" | `Get-Process node \| Stop-Process -Force` |
| "Port 8000 already in use" | `Get-Process python \| Stop-Process -Force` |
| "No data in dashboard" | Ensure backend is running on 8000 |
| "404 on /health" | Check backend URL is `http://localhost:8000` |
| "npm install fails" | Delete `node_modules` and try again |

---

## 📖 Next Steps

1. **Explore Dashboard** - Click through account details
2. **Test API** - Try endpoints in Swagger UI
3. **Review Code** - See [ARCHITECTURE.md](./ARCHITECTURE.md)
4. **Run Tests** - Verify 100% pass rate
5. **Read Docs** - Full details in README.md

---

**That's it! You're now running UPI Mule Detection.**
