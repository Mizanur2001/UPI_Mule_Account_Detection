# 🚨 UPI Mule Account Detection – CSIC Stage III Prototype

This repository contains a **working prototype (MVP-1)** for detecting  
**mule accounts and collusive fraud in UPI transactions**, developed as part of:

> **Cyber Security Innovation Challenge (CSIC) 1.0 – Stage III**  
> Problem Statement: *Mule Accounts & Collusive Fraud in UPI*

---

## 🎯 What This Prototype Does

The system detects mule accounts using a **hybrid approach**:

1. **Behavioral Analysis**
   - Sudden transaction spikes
   - New accounts with rapid activity

2. **Graph-Based Detection**
   - Star patterns (many → one → sink)
   - Chain laundering paths
   - Circular fund movement (loops)

3. **Device Correlation**
   - Same device controlling multiple accounts

All detections are:
- ✅ **Explainable**
- ✅ **Visualized**
- ✅ **Real-time (prototype-level)**

---

## 🗂️ Project Structure

```
upi-mule-detection-mvp/
│
├── data/              # Simulated UPI data
├── backend/           # FastAPI backend (risk engine)
├── dashboard/         # Streamlit visualization
├── docs/              # Architecture & demo flow
├── ppt/               # CSIC presentation
├── report/            # CSIC detailed report
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Prerequisites

- Python **3.10 or 3.11**
- Windows / Linux / macOS
- Git

Check Python version:
```bash
python --version
```

## 🚀 Setup Instructions (Fresh Clone)

### 1️⃣ Clone the Repository
```bash
git clone <your-repo-url>
cd upi-mule-detection-mvp
```

### 2️⃣ Create & Activate Virtual Environment

**Windows (PowerShell)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
If activation is blocked:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

**Linux / macOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## ▶️ Run the Backend (FastAPI)

From project root:
```bash
python -m uvicorn backend.app:app --reload
```
Test in browser:
[http://127.0.0.1:8000/score/mule_loop2@upi](http://127.0.0.1:8000/score/mule_loop2@upi)

## 🖥️ Run the Dashboard (Streamlit)

Open a new terminal, activate venv again, then:
```bash
python -m streamlit run dashboard/dashboard.py
```
Dashboard opens at:
[http://localhost:8501](http://localhost:8501)
