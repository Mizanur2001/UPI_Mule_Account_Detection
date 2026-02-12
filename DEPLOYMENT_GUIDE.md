# UPI Mule Account Detection – Stage III MVP
## Deployment & User Guide

---

## 🚀 QUICK START (2 Minutes)

### Prerequisites
- Python 3.10+ installed
- Windows / Linux / macOS

### Setup

**1. Clone & Navigate**
```bash
cd UPI_Mule_Account_Detection
```

**2. Create Virtual Environment (Windows)**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Run Dashboard**
```bash
python -m streamlit run dashboard/dashboard_optimized.py
```

The dashboard opens automatically at: **http://localhost:8501**

---

## 📊 Dashboard Walkthrough

### Tab 1: Summary
- **Overview metrics** (total accounts, risk counts, averages)
- Risk distribution breakdown
- Component contribution analysis

### Tab 2: Risk Analysis
- **Filter by risk level** (HIGH/MEDIUM/LOW)
- **Set minimum score threshold**
- **Sort by score, confidence, or factors**
- **Drill down** into individual accounts with full evidence
- **Export to CSV** for further investigation

### Tab 3: Network Visualization  
- Interactive **transaction flow graph**
- **Click nodes** to see account details
- **Adjust max nodes** to explore large networks
- **Filter by risk level** to highlight suspicious patterns

### Tab 4: Investigation Report
- Auto-generated **markdown report**
- **Top flagged accounts** with evidence
- Download as `.md` file for documentation

### Tab 5: How It Works
- Detailed explanation of detection algorithm
- Risk scoring formula with examples
- Threshold values and confidence levels

---

## 🔍 Understanding Risk Scores

### Risk Levels
| Level | Range | Meaning |
|-------|-------|---------|
| **HIGH** | 70-100 | Mule account, immediate investigation needed |
| **MEDIUM** | 40-69 | Suspicious patterns, enhanced monitoring |
| **LOW** | 0-39 | Likely legitimate transaction behavior |

### Confidence Levels
- **VERY HIGH** (80+): Strong multi-signal confirmation
- **HIGH** (70+): Clear mule indicators
- **MODERATE** (50+): Multiple warning signs
- **LOW** (40+): Single or weak signals

### Score Components

**Behavioral (30% weight)**
- Transaction velocity (5+ txns = +25-35 pts)
- New account rapid activity (0-7 days = +40 pts)
- Pass-through ratio (80-120% = +35 pts)
- Large amounts (avg > ₹5K = +20 pts)
- Asymmetric flow patterns (+15-35 pts)

**Graph Analysis (50% weight)** [MOST IMPORTANT]
- Star patterns: Many inputs → one output (+30-45 pts)
- Distributor: One input → many outputs (+30-45 pts)
- Chains: Linear laundering paths (+20-35 pts)
- Circular: Fund rotation loops (+50 pts)

**Device (20% weight)**
- Device on 3+ accounts (+15-50 pts)
- Multiple devices on same account (+20-30 pts)

---

## 🎯 Known Test Scenarios in Demo Data

Your test data includes 5 known mule account scenarios:

### 1. Classic Star Aggregator
**Account:** `mule_aggregator@upi`
- **Pattern:** 5 friends send → 1 account → distributor
- **Expected Score:** HIGH (95+)
- **Evidence:** Star pattern + high velocity + pass-through ratio

### 2. Circular Network
**Accounts:** `circle_node_1@upi` through `circle_node_4@upi`
- **Pattern:** A→B→C→D→A (fund rotation loop)
- **Expected Score:** HIGH (90+)
- **Evidence:** Circular network + shared device + mule behavior

### 3. Chain Laundering
**Accounts:** `chain_node_1@upi` through `chain_node_5@upi`
- **Pattern:** Linear path A→B→C→D→E
- **Expected Score:** MEDIUM-HIGH (50-70)
- **Evidence:** Laundering chain detected

### 4. Device Ring
**Accounts:** `device_ring_1@upi` through `device_ring_3@upi`
- **Pattern:** Same device controlling 3 accounts
- **Expected Score:** HIGH (70+)
- **Evidence:** Device concentration + graph patterns

### 5. Rapid Onboarding
**Account:** `new_mule_account@upi`
- **Pattern:** 1-day-old account with 8 rapid transactions
- **Expected Score:** HIGH (80+)
- **Evidence:** New account + velocity + amounts

---

## 🔧 Backend API (For Integration)

If you want to use the API directly (without dashboard):

**Start FastAPI Server:**
```bash
python -m uvicorn backend.app:app --reload
```

**Score Individual Account:**
```
GET http://127.0.0.1:8000/score/{account_id}
```

**Example Response:**
```json
{
  "account_id": "mule_aggregator@upi",
  "risk_score": 95,
  "risk_level": "HIGH",
  "confidence": "VERY HIGH",
  "behavioral_score": 100,
  "graph_score": 85,
  "device_score": 60,
  "reasons": [
    "Star-pattern mule behavior (5 inflows → 1 outflow)",
    "Mule indicator: 95% of inflow sent back out",
    "High transaction velocity (10 txns)",
    "Shared device across multiple accounts"
  ]
}
```

---

## 📁 Project Structure

```
UPI_Mule_Account_Detection/
├── backend/
│   ├── app.py                 # FastAPI entry point
│   ├── api/
│   │   └── score.py          # Scoring endpoint
│   ├── core/
│   │   ├── behavioral.py     # Velocity & temporal detection
│   │   ├── graph_analysis.py # Network pattern detection
│   │   ├── device_risk.py    # Device correlation
│   │   └── risk_engine.py    # Score aggregation
│   └── utils/
│       ├── data_loader.py    # CSV loaders
│       └── helpers.py        # Utilities
├── dashboard/
│   ├── dashboard_optimized.py  # 🆕 Enhanced Streamlit app
│   └── graph_view.py          # Network visualization
├── data/
│   ├── transactions.csv       # UPI transaction records
│   ├── accounts.csv          # Account metadata
│   └── devices.csv           # Device-to-account mapping
├── scripts/
│   └── enhanced_data_generator.py  # 🆕 Mule scenario creator
├── docs/
│   └── demo_flow.md
├── requirements.txt
├── README.md
└── test_backend.py            # 🆕 Backend test script
```

---

## 🧪 Testing

### Backend Tests Only
```bash
python test_backend.py
```

Output will show:
- Import verification
- Data loading stats
- Graph construction
- Batch scoring results
- HIGH risk accounts detected

### Full Dashboard Test
```bash
python -m streamlit run dashboard/dashboard_optimized.py
```

---

## ⚡ Performance Notes

- **Batch scoring:** All accounts in < 2 seconds
- **Graph analysis:** One-pass cycle/chain detection
- **Caching:** Scores cached to avoid re-computation
- **Scalability:** Tested with 50+ accounts; scales linearly

---

## 📝 Customization

### Add More Test Data
Edit `scripts/enhanced_data_generator.py` and add new scenarios:

```python
def create_custom_scenario():
    transactions = []
    devices = []
    accounts = []
    
    # Add your mule pattern here
    # ...
    
    return transactions, accounts, devices
```

Then add to `generate_enhanced_dataset()`:
```python
txns, accs, devs = create_custom_scenario()
all_txns.extend(txns)
all_accounts.extend(accs)
all_devices.extend(devs)
```

Regenerate data:
```bash
python scripts/enhanced_data_generator.py
```

### Adjust Risk Thresholds
Edit thresholds in `backend/core/risk_engine.py`:

```python
def risk_level(score):
    if score >= 70:         # Adjust HIGH threshold
        return "HIGH"
    elif score >= 40:       # Adjust MEDIUM threshold
        return "MEDIUM"
    else:
        return "LOW"
```

### Change Weight Distribution
Edit `backend/core/risk_engine.py`:

```python
base_score = (
    0.30 * behavioral,  # Change from 30%
    0.50 * graph,       # Change from 50%
    0.20 * device       # Change from 20%
)
```

---

## 🐛 Troubleshooting

### Issue: ImportError: DLL load failed
**Solution:** Matplotlib has dependency issues. Use `dashboard_optimized.py` which doesn't require it.

### Issue: Port 8501 already in use
**Solution:** 
```bash
streamlit run dashboard/dashboard_optimized.py --server.port 8502
```

### Issue: No HIGH risk accounts detected
**Solution:** Check that test data was generated:
```bash
python scripts/enhanced_data_generator.py
```

### Issue: Graph rendering is slow
**Solution:** Reduce max_nodes in dashboard or run on faster hardware.

---

## 📧 Support & Feedback

For questions or issues during the Stage III submission:
1. Check test_backend.py output to verify detection logic works
2. Review Tab 5 ("How It Works") for algorithm details
3. Check individual account explanations in Tab 2 for debugging
4. Test with demo scenarios listed above

---

## 🎬 Stage III Submission Checklist

- ✅ Enhanced behavioral analysis (velocity, pass-through, new account patterns)
- ✅ Advanced graph detection (stars, chains, cycles, distributors)
- ✅ Device correlation scoring
- ✅ Multi-signal confidence boosting
- ✅ Professional Streamlit dashboard
- ✅ Filters, sorting, exports (CSV)
- ✅ Detailed explainability (reasons for every score)
- ✅ Report generation
- ✅ Test scenarios with realistic mule patterns
- ✅ FastAPI backend ready for integration
- ✅ Complete documentation

---

**Last Updated:** February 2026  
**MVP Status:** Stage III Ready  
**Deployment:** Production-ready with test data
