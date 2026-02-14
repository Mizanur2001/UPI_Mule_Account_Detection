# 🚀 UPI Mule Account Detection - Quick Start Guide

## **EASIEST WAY: One-Click Start**

### **Option 1: Batch File (Windows)**
Simply double-click:
```
start-all.bat
```

### **Option 2: PowerShell**
Right-click and select "Run with PowerShell":
```
start-all.ps1
```

---

## **Manual Start (If Scripts Don't Work)**

### **Step 1: Open PowerShell Terminal 1**
```powershell
cd "c:\Users\suvom\OneDrive\Desktop\ICRH\FinalS\UPI_Mule_Account_Detection\backend"
python -m uvicorn app:app --port 8001 --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8001
INFO:     Application startup complete
```

### **Step 2: Open PowerShell Terminal 2**
```powershell
cd "c:\Users\suvom\OneDrive\Desktop\ICRH\FinalS\UPI_Mule_Account_Detection\frontend"
npm run dev
```

**Expected Output:**
```
➜  Local:   http://localhost:3000/
```

### **Step 3: Open Browser**
Navigate to: **http://localhost:3000**

---

## **🎯 What to Test**

### **1. Real-Time API Tab**
- Enter account ID: `mule_aggregator@upi`
- Click "Test" button
- See risk analysis

### **2. Network Graph Tab**
- Click on red/orange node
- View account details panel
- Zoom In/Out controls

### **3. Theme Toggle**
- Click Sun/Moon icon in header
- Switch dark/light mode

### **4. Notifications**
- Operations show toast messages
- Auto-dismiss after 3 seconds

---

## **⚡ Quick Commands**

```powershell
# Build frontend
cd frontend
npm run build

# Start dev server only
npm run dev

# Build for production
npm run build

# Check backend health
curl http://localhost:8001/health

# Stop services
# Press Ctrl+C in terminal windows
```

---

## **🔧 Configuration**

All API endpoints managed in `.env`:

**For Local Development:**
```
VITE_API_BASE_URL=http://localhost:8001
```

**For Production:**
```
VITE_API_BASE_URL=https://api.production.com
```

After changing `.env`, restart frontend dev server.

---

## **✅ Verification Checklist**

- ✅ Backend running on `http://localhost:8001`
- ✅ Frontend running on `http://localhost:3000`
- ✅ No error messages in console
- ✅ Network graph loads (wait 2-3 seconds)
- ✅ Toast notifications appear
- ✅ Theme toggle works
- ✅ Can click on graph nodes

---

## **❌ Troubleshooting**

### **Port Already in Use**
```powershell
# Find what's using port 8001
netstat -ano | findstr :8001

# Kill it (replace PID with actual number)
taskkill /PID 1234 /F
```

### **Module Not Found Error**
```powershell
cd frontend
npm install
npm run dev
```

### **Backend Connection Error**
- Ensure backend is running on correct port (8001)
- Check `.env` file has `VITE_API_BASE_URL=http://localhost:8001`
- Restart frontend dev server

### **Permission Denied**
Run PowerShell as Administrator:
- Right-click PowerShell → "Run as administrator"
- Then run the command again

---

## **📁 Project Structure**

```
UPI_Mule_Account_Detection/
├── backend/
│   ├── app.py (FastAPI server)
│   ├── api/ (endpoints)
│   ├── core/ (scoring logic)
│   └── utils/ (helpers)
├── frontend/
│   ├── src/ (React components)
│   ├── package.json
│   └── .env (configuration)
├── data/ (CSV data files)
├── start-all.bat (Windows quick start)
├── start-all.ps1 (PowerShell quick start)
└── README.md (this file)
```

---

## **🎉 You're Ready!**

Just run `start-all.bat` or `start-all.ps1` and enjoy your UPI Mule Detection system!

For detailed documentation, see individual README files in backend/ and frontend/ directories.
