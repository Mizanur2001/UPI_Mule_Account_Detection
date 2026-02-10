import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import os
import networkx as nx

# --------------------------------
# Import backend scoring logic
# --------------------------------
from backend.api.score import batch_score_accounts
from backend.utils.data_loader import load_accounts, load_devices
from backend.core.graph_analysis import build_transaction_graph

# --------------------------------
# Streamlit Page Config
# --------------------------------
st.set_page_config(
    page_title="UPI Mule Account Detection Dashboard",
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
# Resource Loading (Cached)
# --------------------------------
@st.cache_resource(show_spinner="Loading data models & building graph...")
def load_all_resources():
    # Load Transactions
    txns = pd.read_csv("data/transactions.csv")
    txns["sender"] = txns["sender"].astype(str)
    txns["receiver"] = txns["receiver"].astype(str)

    # Load other metadata
    accounts = load_accounts()
    devices = load_devices()

    # Build Graph once (vectorized, fast)
    G = build_transaction_graph(txns)

    # Precompute unique accounts
    unique_accounts = sorted(
        set(txns["sender"].dropna()) | set(txns["receiver"].dropna())
    )

    # Batch-score ALL accounts in one pass
    # (graph cycle detection runs once, not per-account)
    scores = batch_score_accounts(unique_accounts, txns, accounts, devices, G)

    return txns, accounts, devices, G, unique_accounts, scores

# Load resources
txns, accounts, devices, G, unique_accounts, scores = load_all_resources()

# --------------------------------
# Top Metrics
# --------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Transactions", len(txns))

with col2:
    st.metric("Unique Accounts", len(unique_accounts))

with col3:
    high_risk = sum(1 for s in scores.values() if s["risk_level"] == "HIGH")
    st.metric("High Risk Accounts", high_risk)

# --------------------------------
# Transaction Table
# --------------------------------
st.subheader("📄 Transaction Data")
st.dataframe(txns, width="stretch")

# --------------------------------
# Lazy-load Graph (IMPORTANT)
# --------------------------------
st.subheader("🕸️ Risk-Aware Transaction Network")

# Controls for scalability
gcol1, gcol2 = st.columns([1, 3])
with gcol1:
    show_graph = st.checkbox(
        "Show transaction network graph",
        value=False,
    )
with gcol2:
    max_nodes = st.slider(
        "Max nodes to display",
        min_value=20,
        max_value=min(len(unique_accounts), 500),
        value=min(len(unique_accounts), 100),
        step=10,
        help="Limit nodes for large datasets to keep the graph responsive.",
    )

if show_graph:
    with st.spinner("Rendering graph..."):
        # Prioritise high-risk accounts so they always appear
        sorted_accounts = sorted(
            unique_accounts,
            key=lambda a: scores.get(a, {}).get("risk_score", 0),
            reverse=True,
        )
        visible_accounts = set(sorted_accounts[:max_nodes])

        net = Network(
            height="550px",
            width="100%",
            directed=True,
            notebook=False,
            bgcolor="#ffffff",
        )

        # ----------------------------
        # Add Nodes with Risk Styling (from precomputed scores)
        # ----------------------------
        for acc in visible_accounts:
            result = scores.get(acc, {"risk_score": 0, "risk_level": "LOW", "reasons": []})

            score_val = result["risk_score"]
            level = result["risk_level"]
            reasons = result.get("reasons", [])

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
                f"<b>Account:</b> {acc}<br>"
                f"<b>Risk Score:</b> {score_val}<br>"
                f"<b>Risk Level:</b> {level}<br><br>"
                f"<b>Reasons:</b><br>"
                + "<br>".join(reasons)
            )

            net.add_node(
                acc,
                label=acc,
                color=color,
                size=size,
                title=tooltip,
            )

        # ----------------------------
        # Add Edges (only between visible nodes)
        # ----------------------------
        for _, row in txns.iterrows():
            s, r = str(row["sender"]), str(row["receiver"])
            if s in visible_accounts and r in visible_accounts:
                net.add_edge(s, r, value=row["amount"])

        # ----------------------------
        # Render Graph (Windows Safe)
        # ----------------------------
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
            net.save_graph(tmp.name)
            html_path = tmp.name

        with open(html_path, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=600, scrolling=True)

        os.remove(html_path)

        if len(unique_accounts) > max_nodes:
            st.info(
                f"Showing top {max_nodes} accounts (sorted by risk). "
                f"Increase the slider to see more."
            )

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
   - Star aggregation patterns
   - Chain laundering paths
   - Circular fund movement (loops)

3. **Device Correlation**
   - Same device controlling multiple accounts

When multiple signals correlate, the system **boosts confidence**  
to strongly flag organized mule networks while keeping false positives low.
"""
)

st.success("✅ Prototype ready for CSIC Stage-III demo")