import streamlit as st
import pandas as pd
from pyvis.network import Network
import tempfile
import os
import networkx as nx
import matplotlib.pyplot as plt
from datetime import datetime

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
    page_title="UPI Mule Detection - Stage III MVP",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚨 UPI Mule Account Detection Dashboard – Stage III MVP")
st.markdown(
    """
**Real-time detection of mule accounts and collusive fraud in UPI transactions.**  
Using behavioral analysis, graph patterns, and device correlation.
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
    scores = batch_score_accounts(unique_accounts, txns, accounts, devices, G)

    return txns, accounts, devices, G, unique_accounts, scores

# Load resources
txns, accounts, devices, G, unique_accounts, scores = load_all_resources()

# Convert scores to DataFrame for easier analysis
scores_df = pd.DataFrame([
    {
        "Account": acc,
        "Risk Score": result["risk_score"],
        "Risk Level": result["risk_level"],
        "Confidence": result.get("confidence", "N/A"),
        "Behavioral": result.get("behavioral_score", 0),
        "Graph": result.get("graph_score", 0),
        "Device": result.get("device_score", 0),
        "Reasons": " | ".join(result["reasons"][:3])  # Top 3 reasons
    }
    for acc, result in scores.items()
])

scores_df = scores_df.sort_values("Risk Score", ascending=False)

# ================================
# DASHBOARD TABS
# ================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Summary & Stats",
    "🎯 Account Risk Analysis", 
    "🕸️ Transaction Network",
    "📋 Detailed Report",
    "ℹ️ How It Works"
])

# ================================
# TAB 1: SUMMARY & STATISTICS
# ================================
with tab1:
    st.subheader("Risk Summary Dashboard")
    
    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    high_risk_count = sum(1 for s in scores.values() if s["risk_level"] == "HIGH")
    medium_risk_count = sum(1 for s in scores.values() if s["risk_level"] == "MEDIUM")
    low_risk_count = sum(1 for s in scores.values() if s["risk_level"] == "LOW")
    avg_risk = scores_df["Risk Score"].mean()
    
    with col1:
        st.metric("Total Accounts", len(unique_accounts), delta=None)
    with col2:
        st.metric("🔴 High Risk", high_risk_count, delta=f"{high_risk_count/len(unique_accounts)*100:.1f}%")
    with col3:
        st.metric("🟠 Medium Risk", medium_risk_count, delta=f"{medium_risk_count/len(unique_accounts)*100:.1f}%")
    with col4:
        st.metric("🟢 Low Risk", low_risk_count, delta=f"{low_risk_count/len(unique_accounts)*100:.1f}%")
    with col5:
        st.metric("📈 Avg Risk Score", f"{avg_risk:.1f}/100", delta=None)
    
    # Risk Distribution Chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Risk Distribution")
        risk_counts = scores_df["Risk Level"].value_counts()
        colors_map = {"HIGH": "#ff0000", "MEDIUM": "#ff9900", "LOW": "#0099ff"}
        fig, ax = plt.subplots(figsize=(6, 4))
        risk_counts.plot(kind="bar", color=[colors_map.get(x, "#999999") for x in risk_counts.index], ax=ax)
        ax.set_ylabel("Number of Accounts")
        ax.set_xlabel("Risk Level")
        ax.set_title("Account Risk Distribution")
        plt.xticks(rotation=0)
        st.pyplot(fig, use_container_width=True)
    
    with col2:
        st.subheader("Risk Score Distribution")
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(scores_df["Risk Score"], bins=20, color="#ff6600", edgecolor="black")
        ax.axvline(x=70, color="red", linestyle="--", label="HIGH threshold")
        ax.axvline(x=40, color="orange", linestyle="--", label="MEDIUM threshold")
        ax.set_xlabel("Risk Score")
        ax.set_ylabel("Number of Accounts")
        ax.set_title("Score Distribution")
        ax.legend()
        st.pyplot(fig, use_container_width=True)
    
    # Score Component Heatmap
    st.subheader("Average Risk Component Contribution")
    component_avg = pd.DataFrame({
        "Behavioral": [scores_df["Behavioral"].mean()],
        "Graph": [scores_df["Graph"].mean()],
        "Device": [scores_df["Device"].mean()]
    })
    
    fig, ax = plt.subplots(figsize=(8, 2))
    component_avg.T.plot(kind="bar", ax=ax, legend=False, color="#4499ff")
    ax.set_ylabel("Average Score Contribution")
    ax.set_title("Risk Factor Contribution (Average across all accounts)")
    plt.xticks(rotation=0)
    st.pyplot(fig, use_container_width=True)


# ================================
# TAB 2: ACCOUNT RISK ANALYSIS
# ================================
with tab2:
    st.subheader("🎯 Account Risk Scoring Table")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_risk_level = st.multiselect(
            "Filter by Risk Level",
            ["HIGH", "MEDIUM", "LOW"],
            default=["HIGH", "MEDIUM", "LOW"],
            key="risk_level_filter"
        )
    
    with col2:
        min_score = st.slider("Minimum Risk Score", 0, 100, 0, key="min_score_filter")
    
    with col3:
        sort_by = st.selectbox("Sort by", ["Risk Score (High→Low)", "Risk Score (Low→High)", "Confidence", "Behavioral", "Graph", "Device"])
    
    # Apply filters
    filtered_df = scores_df[
        (scores_df["Risk Level"].isin(selected_risk_level)) &
        (scores_df["Risk Score"] >= min_score)
    ]
    
    # Apply sorting
    sort_map = {
        "Risk Score (High→Low)": ("Risk Score", False),
        "Risk Score (Low→High)": ("Risk Score", True),
        "Confidence": ("Confidence", False),
        "Behavioral": ("Behavioral", False),
        "Graph": ("Graph", False),
        "Device": ("Device", False)
    }
    sort_col, ascending = sort_map[sort_by]
    filtered_df = filtered_df.sort_values(sort_col, ascending=ascending)
    
    st.write(f"**Showing {len(filtered_df)} of {len(scores_df)} accounts**")
    
    # Display table with color coding
    def color_risk_level(val):
        if val == "HIGH":
            return "background-color: #ffcccc"
        elif val == "MEDIUM":
            return "background-color: #ffeecc"
        else:
            return "background-color: #ccffcc"
    
    def color_score(val):
        if val >= 70:
            return "color: white; background-color: #ff0000"
        elif val >= 40:
            return "color: black; background-color: #ff9900"
        else:
            return "color: black; background-color: #0099ff"
    
    styled_df = filtered_df.copy()
    styled_df = styled_df.style.map(color_risk_level, subset=["Risk Level"])
    styled_df = styled_df.map(color_score, subset=["Risk Score"])
    
    st.dataframe(styled_df, use_container_width=True)
    
    # Expandable details
    st.subheader("📄 Account Details")
    selected_account = st.selectbox("Select account to view details", filtered_df["Account"].tolist())
    
    if selected_account:
        account_score = scores[selected_account]
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Risk Score", account_score["risk_score"])
            st.metric("Risk Level", account_score["risk_level"])
            st.metric("Confidence", account_score.get("confidence", "N/A"))
        
        with col2:
            st.metric("Behavioral Score", account_score.get("behavioral_score", 0))
            st.metric("Graph Score", account_score.get("graph_score", 0))
            st.metric("Device Score", account_score.get("device_score", 0))
        
        st.subheader("Risk Factors (Evidence)")
        for i, reason in enumerate(account_score["reasons"], 1):
            st.write(f"{i}. {reason}")
    
    # Export functionality
    st.subheader("📥 Export Results")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download High/Medium Risk Accounts (CSV)",
            data=csv_data,
            file_name=f"mule_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Summary export
        summary_text = f"""UPI MULE ACCOUNT DETECTION REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

=== SUMMARY ===
Total Accounts Analyzed: {len(unique_accounts)}
High Risk Accounts: {high_risk_count}
Medium Risk Accounts: {medium_risk_count}
Low Risk Accounts: {low_risk_count}
Average Risk Score: {avg_risk:.2f}/100

=== FLAGGED ACCOUNTS (HIGH) ===
"""
        for _, row in filtered_df[filtered_df["Risk Level"] == "HIGH"].iterrows():
            summary_text += f"\n{row['Account']}: {row['Risk Score']}/100 - {row['Reasons'][:100]}..."
        
        st.download_button(
            label="📋 Download Summary Report (TXT)",
            data=summary_text,
            file_name=f"mule_detection_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )


# ================================
# TAB 3: TRANSACTION NETWORK
# ================================
with tab3:
    st.subheader("🕸️ Risk-Aware Transaction Network Visualization")
    
    # Graph controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_graph = st.checkbox("Render Network Graph", value=True)
    
    with col2:
        max_nodes = st.slider(
            "Max nodes to display",
            min_value=20,
            max_value=min(len(unique_accounts), 500),
            value=min(len(unique_accounts), 80),
            step=10
        )
    
    with col3:
        min_risk_filter = st.selectbox("Show accounts with risk level", ["ALL", "HIGH+MEDIUM", "HIGH only"])
    
    if show_graph:
        with st.spinner("Rendering graph..."):
            # Filter accounts for display
            if min_risk_filter == "HIGH only":
                visible_accounts = set([a for a in unique_accounts if scores.get(a, {}).get("risk_level") == "HIGH"][:max_nodes])
            elif min_risk_filter == "HIGH+MEDIUM":
                visible_accounts = set([a for a in unique_accounts if scores.get(a, {}).get("risk_level") in ["HIGH", "MEDIUM"]][:max_nodes])
            else:
                sorted_accounts = sorted(unique_accounts, key=lambda a: scores.get(a, {}).get("risk_score", 0), reverse=True)
                visible_accounts = set(sorted_accounts[:max_nodes])

            net = Network(
                height="700px",
                width="100%",
                directed=True,
                notebook=False,
                bgcolor="#ffffff",
            )

            # Add nodes with risk styling
            for acc in visible_accounts:
                result = scores.get(acc, {"risk_score": 0, "risk_level": "LOW", "reasons": []})
                score_val = result["risk_score"]
                level = result["risk_level"]
                reasons = result.get("reasons", [])

                if level == "HIGH":
                    color = "#ff0000"
                    size = 40
                elif level == "MEDIUM":
                    color = "#ff9900"
                    size = 25
                else:
                    color = "#0099ff"
                    size = 15

                tooltip = (
                    f"<b>Account:</b> {acc}<br>"
                    f"<b>Risk Score:</b> {score_val}<br>"
                    f"<b>Risk Level:</b> {level}<br><br>"
                    f"<b>Evidence:</b><br>"
                    + "<br>".join([f"• {r}" for r in reasons[:5]])
                )

                net.add_node(acc, label=acc, color=color, size=size, title=tooltip)

            # Add edges
            for _, row in txns.iterrows():
                s, r = str(row["sender"]), str(row["receiver"])
                if s in visible_accounts and r in visible_accounts:
                    net.add_edge(s, r, value=row["amount"], title=f"₹{row['amount']:,.0f}")

            # Render
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                html_path = tmp.name

            with open(html_path, "r", encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=750, scrolling=True)

            os.remove(html_path)

            if len(visible_accounts) < len(unique_accounts):
                st.info(f"📌 Showing {len(visible_accounts)} nodes (adjust slider for more)")
    
    # Legend
    st.subheader("🎨 Legend")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🔴 **Red** = High Risk Mule Account")
    with col2:
        st.markdown("🟠 **Orange** = Medium Risk (Suspicious)")
    with col3:
        st.markdown("🔵 **Blue** = Low Risk (Likely Legitimate)")


# ================================
# TAB 4: DETAILED REPORT
# ================================
with tab4:
    st.subheader("📋 Detailed Investigation Report")
    
    # Generate report
    report = f"""
# UPI MULE ACCOUNT DETECTION REPORT
**Stage III MVP – Prototype Report**

---

## Executive Summary
- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Accounts Analyzed:** {len(unique_accounts)}
- **Total Transactions:** {len(txns)}
- **Average Risk Score:** {avg_risk:.2f}/100

---

## Detection Summary
- **🔴 HIGH RISK:** {high_risk_count} accounts ({high_risk_count/len(unique_accounts)*100:.1f}%)
- **🟠 MEDIUM RISK:** {medium_risk_count} accounts ({medium_risk_count/len(unique_accounts)*100:.1f}%)
- **🟢 LOW RISK:** {low_risk_count} accounts ({low_risk_count/len(unique_accounts)*100:.1f}%)

---

## Methodology
The system detects mule accounts using three independent signals:

### 1. Behavioral Analysis (30% weight)
- Transaction velocity detection
- New account rapid activity monitoring
- Amount anomalies
- Asymmetric inflow/outflow patterns

### 2. Graph Analysis (50% weight) [HIGHEST PRIORITY]
- Star patterns: Multiple inputs → Single output
- Distributor patterns: Single input → Multiple outputs
- Chain detection: Money laundering paths
- Circular networks: Fund rotation schemes

### 3. Device Correlation (20% weight)
- Device concentration risk
- Multi-device control patterns
- Account clustering by device

---

## Top 10 Flagged Accounts
"""
    
    high_risk_accounts = scores_df[scores_df["Risk Level"] == "HIGH"].head(10)
    for i, (_, row) in enumerate(high_risk_accounts.iterrows(), 1):
        report += f"\n### {i}. {row['Account']} (Score: {row['Risk Score']}/100)\n"
        account_details = scores[row['Account']]
        for reason in account_details['reasons'][:3]:
            report += f"- {reason}\n"
    
    report += f"""

---

## Recommendations
1. **Immediate Investigation:** Review all HIGH risk accounts for suspicious activity
2. **Enhanced Monitoring:** Apply real-time alerts for medium-risk accounts
3. **Device Analysis:** Cross-reference device IDs for coordinated networks
4. **Transaction Blocking:** Consider blocking transactions from confirmed mule networks

---

*Auto-generated by UPI Mule Detection MVP*
"""
    
    st.markdown(report)
    
    st.download_button(
        label="📥 Download Full Report (Markdown)",
        data=report,
        file_name=f"mule_detection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )


# ================================
# TAB 5: HOW IT WORKS
# ================================
with tab5:
    st.subheader("ℹ️ How the Detection System Works")
    
    st.markdown("""
## System Architecture

### Three Independent Risk Signals

#### 🔍 Signal 1: Behavioral Analysis (30%)
Detects individual account misbehavior:
- **High velocity:** 5+ transactions in short time
- **New account fraud:** 0-7 days old with rapid activity  
- **Pass-through pattern:** Receives and immediately sends out similar amounts
- **Large amounts:** Average > ₹5,000 or single txn > ₹10,000

#### 🕸️ Signal 2: Graph Analysis (50%) [MOST IMPORTANT]
Detects network-based mule patterns:
- **Star Aggregators:** Many accounts send to ONE account (3+ → 1)
  - High intensity: 5+ inflows → 1 outflow
- **Distributors:** ONE account sends to many (1 → 3+)
- **Chain Laundering:** Account in transaction path (A→B→C→D)
- **Circular Networks:** Money rotates in a loop (A→B→C→A)

#### 📱 Signal 3: Device Risk (20%)
Detects coordinated fraud:
- **Device concentration:** Same device on 3+ accounts
- **Multi-device control:** Account accessed from 5+ devices

### Risk Scoring Formula

```
Base Score = (0.30 × Behavioral) + (0.50 × Graph) + (0.20 × Device)

Final Score = Base Score + Boost

Boost Rules:
- Graph ≥ 30 + Device ≥ 15: +15
- Behavioral ≥ 30 + Graph ≥ 30: +12
- All three signals present: +10
- Extreme correlation (all ≥ 40): +15
```

### Risk Classification

| Risk Level | Score | Action |
|:-----------|:------|:-------|
| **HIGH** | 70-100 | Immediate investigation required |
| **MEDIUM** | 40-69 | Enhanced monitoring recommended |
| **LOW** | 0-39 | Routine monitoring |

### Key Features
✅ **Real-time Scoring** – FastAPI backend processes accounts instantly  
✅ **Explainable** – Every flag includes specific evidence  
✅ **Scalable** – Batch processing handles large datasets  
✅ **Accurate** – Multi-signal fusion reduces false positives  

### Data Inputs
- **Transactions:** sender, receiver, amount
- **Accounts:** account_id, account_age_days
- **Devices:** account_id, device_id

---

## Demo Scenarios

### Example 1: Classic Mule (Star Aggregator)
- **Alice** receives payments from 8 friends → sends to 1 "supplier"
- **Detection:** High graph score (star pattern) + device concentration
- **Result:** HIGH RISK ✋

### Example 2: New Account Onboarding Fraud  
- **Bob** account created 3 days ago
- Makes 6 transactions with average ₹7,000
- **Detection:** High behavioral score (new + velocity) + graph score
- **Result:** HIGH RISK ✋

### Example 3: Legitimate Small Business
- **Charlie** receives payments from suppliers, sends to retailers
- 4-5 transactions/day, consistent patterns
- No circular paths, different devices
- **Detection:** Moderate behavioral + device score, no graph patterns
- **Result:** LOW RISK ✅

---

## Performance
- ⚡ Batch scoring: All accounts in < 2 seconds
- 📊 Graph analysis: Optimized DFS (O(V·depth_limit))
- 💾 Caching: Pre-computed scores for instant dashboard

## Stage III Improvements (This MVP)
✅ Enhanced behavioral analysis with pass-through ratios  
✅ Improved graph patterns with intensity metrics  
✅ Device risk with concentration analysis  
✅ Professional dashboard with filters & exports  
✅ Detailed explainability for every score  
✅ Summary statistics & risk distribution charts  
""")
    
    st.info("🎯 This MVP demonstrates core detection logic ready for production deployment with additional data and refinement.")
