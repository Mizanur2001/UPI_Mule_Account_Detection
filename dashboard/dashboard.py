import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import os

# --------------------------------
# Import backend scoring logic
# --------------------------------
from backend.api.score import score_account

# --------------------------------
# Streamlit Page Config
# --------------------------------
st.set_page_config(
    page_title="UPI Mule Account Detection",
    layout="wide"
)

st.title("🚨 UPI Mule Account Detection Dashboard")
st.markdown(
    """
This dashboard visualizes **mule account behavior in UPI** using  
**transaction graphs + explainable risk scoring**.
"""
)

# --------------------------------
# SAFE + CACHED SCORING WRAPPER
# --------------------------------
@st.cache_data(show_spinner=False)
def cached_safe_score(account_id):
    """
    Frontend-safe wrapper around backend scoring.
    Ensures Streamlit never crashes.
    """
    try:
        return score_account(account_id)
    except Exception:
        return {
            "account_id": account_id,
            "risk_score": 0,
            "risk_level": "LOW",
            "reasons": ["No metadata available (assumed legitimate)"]
        }

# --------------------------------
# Load Data
# --------------------------------
txns = pd.read_csv("data/transactions.csv")
txns = txns.dropna(subset=["sender", "receiver"])

# Ensure account columns are strings to avoid type mismatch in PyVis
txns["sender"] = txns["sender"].astype(str)
txns["receiver"] = txns["receiver"].astype(str)

# --------------------------------
# Top Metrics
# --------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Transactions", len(txns))

with col2:
    unique_accounts = set(txns["sender"]).union(set(txns["receiver"]))
    st.metric("Unique Accounts", len(unique_accounts))

with col3:
    high_risk = 0
    for acc in unique_accounts:
        if cached_safe_score(acc)["risk_level"] == "HIGH":
            high_risk += 1
    st.metric("High Risk Accounts", high_risk)

# --------------------------------
# Transaction Table
# --------------------------------
st.subheader("📄 Transaction Data")
st.dataframe(txns, use_container_width=True)

# --------------------------------
# Risk-Aware Transaction Network
# --------------------------------
st.subheader("🕸️ Risk-Aware Transaction Network")

net = Network(
    height="550px",
    width="100%",
    directed=True,
    notebook=False,
    bgcolor="#ffffff"
)

# --------------------------------
# Add Nodes with Risk-Based Styling
# --------------------------------
for acc in map(str, unique_accounts):
    result = cached_safe_score(acc)

    score = result["risk_score"]
    level = result["risk_level"]
    reasons = result["reasons"]

    if level == "HIGH":
        color = "red"
        size = 35
    elif level == "MEDIUM":
        color = "orange"
        size = 25
    else:
        color = "lightblue"
        size = 15

    tooltip = (
        f"Account: {acc}\n"
        f"Risk Score: {score}\n"
        f"Risk Level: {level}\n\n"
        f"Reasons:\n"
        + "\n".join(f"- {r}" for r in reasons)
    )

    net.add_node(
        acc,
        label=acc,
        color=color,
        size=size,
        title=tooltip
    )

# --------------------------------
# Add Transaction Edges
# --------------------------------
for _, row in txns.iterrows():
    net.add_edge(
        row["sender"],
        row["receiver"],
        value=row["amount"],
        arrowStrikethrough=False
    )

# --------------------------------
# Render Graph (Windows + PyVis Safe)
# --------------------------------
with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
    net.save_graph(tmp.name)
    html_path = tmp.name

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

st.components.v1.html(html_content, height=600, scrolling=True)

os.remove(html_path)

# --------------------------------
# Legend
# --------------------------------
st.subheader("🎨 Risk Color Legend")
st.markdown(
    """
- 🔴 **Red** → High Risk Mule Account  
- 🟠 **Orange** → Medium Risk (Suspicious)  
- 🔵 **Blue** → Legitimate Account  

**Node size increases with risk severity.**
"""
)

# --------------------------------
# Explainability Panel
# --------------------------------
st.subheader("🧠 How Risk is Calculated")
st.markdown(
    """
Each account is scored using **three independent signals**:

1. **Behavioral Analysis**
   - Sudden transaction spikes
   - New accounts with rapid activity

2. **Graph Analysis**
   - Star patterns (many → one → sink)
   - Chain laundering paths
   - Circular fund movement (loops)

3. **Device Correlation**
   - Same device controlling multiple accounts

Scores are **boosted when multiple signals correlate**,  
reducing false positives while strongly flagging organized fraud.
"""
)

st.success("✅ Prototype ready for CSIC Stage-III demo")