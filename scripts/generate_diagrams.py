"""
FinGuard Diagram Generator
===========================
Generates beautiful B/W diagrams for the FINAL_REPORT.
All output goes to docs/diagrams/ as PNG files.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ArrowStyle
import matplotlib.patheffects as pe
import numpy as np
import networkx as nx
import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "diagrams")
os.makedirs(OUT_DIR, exist_ok=True)

# ── Global style ──────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Segoe UI', 'Arial', 'Helvetica'],
    'font.size': 11,
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.3,
})

DARK = '#1a1a1a'
MID = '#444444'
LIGHT = '#888888'
BORDER = '#2a2a2a'
BG_LIGHT = '#f5f5f5'
BG_MED = '#e0e0e0'


def draw_box(ax, x, y, w, h, text, fontsize=10, bold=False, fill='#f0f0f0',
             border_color=BORDER, text_color=DARK, corner=0.05, lw=1.5):
    """Draw a rounded rectangle with centered text."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad={corner}",
                         facecolor=fill, edgecolor=border_color, linewidth=lw)
    ax.add_patch(box)
    weight = 'bold' if bold else 'normal'
    ax.text(x + w/2, y + h/2, text, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color=text_color, wrap=True)
    return box


def draw_arrow(ax, x1, y1, x2, y2, color=MID, style='->', lw=1.5):
    """Draw an arrow between two points."""
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw))


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 1: High-Level System Flow
# ═══════════════════════════════════════════════════════════════════════
def diagram_system_flow():
    fig, ax = plt.subplots(1, 1, figsize=(14, 4.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.5)
    ax.axis('off')
    ax.set_title('FinGuard: High-Level System Flow', fontsize=14, fontweight='bold',
                 color=DARK, pad=15)

    # Boxes left to right
    boxes = [
        (0.3, 1.5, 2.0, 1.5, 'UPI\nTransaction\nStream', '#e8e8e8'),
        (3.0, 1.5, 2.0, 1.5, 'Data\nIngestion\nLayer', '#f0f0f0'),
        (5.7, 1.5, 2.2, 1.5, '5-Signal\nDetection\nEngine', '#d8d8d8'),
        (8.6, 1.5, 2.0, 1.5, 'Risk\nAggregation\n& Boosting', '#e8e8e8'),
        (11.3, 1.5, 2.2, 1.5, 'Dashboard\n& API\nResponse', '#f0f0f0'),
    ]
    for (x, y, w, h, txt, fill) in boxes:
        draw_box(ax, x, y, w, h, txt, fontsize=10, bold=True, fill=fill)

    # Arrows
    for i in range(4):
        x1 = boxes[i][0] + boxes[i][2]
        x2 = boxes[i+1][0]
        y = boxes[i][1] + boxes[i][3]/2
        draw_arrow(ax, x1 + 0.05, y, x2 - 0.05, y, lw=2)

    # Labels under arrows
    labels = ['Parse &\nValidate', 'Score\nAccount', 'Weighted\nEnsemble', 'Serve\nResults']
    for i, lbl in enumerate(labels):
        mid_x = (boxes[i][0] + boxes[i][2] + boxes[i+1][0]) / 2
        ax.text(mid_x, 1.2, lbl, ha='center', va='top', fontsize=8, color=LIGHT, style='italic')

    # Sub-label for detection engine
    ax.text(boxes[2][0] + boxes[2][2]/2, 0.9, 'Behavioral | Graph | Device | Temporal | ML',
            ha='center', va='top', fontsize=8, color=MID)

    fig.savefig(os.path.join(OUT_DIR, '01_system_flow.png'))
    plt.close(fig)
    print("[+] 01_system_flow.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 2: System Architecture (Layered)
# ═══════════════════════════════════════════════════════════════════════
def diagram_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(13, 10))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 10)
    ax.axis('off')
    ax.set_title('FinGuard: System Architecture', fontsize=15, fontweight='bold',
                 color=DARK, pad=15)

    # Layer 1: Frontend (top)
    draw_box(ax, 0.5, 8.3, 12, 1.3, '', fill='#eeeeee', lw=2)
    ax.text(6.5, 9.25, 'FRONTEND  (React 18 + Vite)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK)
    tabs = ['Command\nCenter', 'Risk\nAnalysis', 'ML\nInsights', 'Network\nGraph',
            'Timeline', 'Real-Time\nAPI', 'About']
    for i, tab in enumerate(tabs):
        x = 1.0 + i * 1.65
        draw_box(ax, x, 8.4, 1.4, 0.7, tab, fontsize=7, fill='#dcdcdc')

    draw_arrow(ax, 6.5, 8.3, 6.5, 7.6, lw=2, style='<->')

    # Layer 2: API Gateway
    draw_box(ax, 0.5, 6.3, 12, 1.2, '', fill='#e4e4e4', lw=2)
    ax.text(6.5, 7.15, 'API GATEWAY  (FastAPI v2.1.0)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK)
    features = ['API-Key Auth', 'Rate Limiter\n(120/min)', 'CORS', 'Audit Log',
                '11 Endpoints', 'Telemetry']
    for i, feat in enumerate(features):
        x = 0.8 + i * 2.0
        draw_box(ax, x, 6.35, 1.7, 0.6, feat, fontsize=7.5, fill='#d0d0d0')

    draw_arrow(ax, 6.5, 6.3, 6.5, 5.65, lw=2, style='->')

    # Layer 3: Detection Engine (5 modules)
    draw_box(ax, 0.5, 3.8, 12, 1.8, '', fill='#f2f2f2', lw=2)
    ax.text(6.5, 5.3, '5-FACTOR DETECTION ENGINE', ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK)
    modules = [
        ('Behavioral\n(25%)', '#d9d9d9'),
        ('Graph\nAnalytics\n(40%)', '#c5c5c5'),
        ('Device\nFingerprint\n(15%)', '#d9d9d9'),
        ('Temporal\nAnalysis\n(10%)', '#c5c5c5'),
        ('ML Anomaly\nDetection\n(10%)', '#d9d9d9'),
    ]
    for i, (name, fill) in enumerate(modules):
        x = 0.8 + i * 2.4
        draw_box(ax, x, 3.9, 2.1, 1.1, name, fontsize=8.5, bold=True, fill=fill)

    draw_arrow(ax, 6.5, 3.8, 6.5, 3.15, lw=2, style='->')

    # Layer 4: Risk Aggregation
    draw_box(ax, 0.5, 2.0, 12, 1.1, '', fill='#e8e8e8', lw=2)
    ax.text(6.5, 2.7, 'RISK AGGREGATION & CONFIDENCE BOOSTING', ha='center', va='center',
            fontsize=11, fontweight='bold', color=DARK)
    agg_items = ['Weighted Sum', 'Multi-Signal\nBoost (+8 to +20)', 'Risk Classification\n(CRITICAL/HIGH/\nMEDIUM/LOW)']
    for i, item in enumerate(agg_items):
        x = 1.5 + i * 3.5
        draw_box(ax, x, 2.05, 3.0, 0.55, item, fontsize=8, fill='#d5d5d5')

    draw_arrow(ax, 6.5, 2.0, 6.5, 1.35, lw=2, style='->')

    # Layer 5: Data Layer
    draw_box(ax, 0.5, 0.2, 12, 1.1, '', fill='#dcdcdc', lw=2)
    ax.text(6.5, 0.95, 'DATA LAYER', ha='center', va='center',
            fontsize=11, fontweight='bold', color=DARK)
    data_items = ['transactions.csv', 'accounts.csv', 'devices.csv', 'NetworkX Graph\n(in-memory)', 'Model Store\n(pickle)']
    for i, item in enumerate(data_items):
        x = 0.7 + i * 2.4
        draw_box(ax, x, 0.25, 2.1, 0.5, item, fontsize=7.5, fill='#c8c8c8')

    fig.savefig(os.path.join(OUT_DIR, '02_architecture.png'))
    plt.close(fig)
    print("[+] 02_architecture.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 3: Graph Patterns (Star, Chain, Circular)
# ═══════════════════════════════════════════════════════════════════════
def diagram_graph_patterns():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle('Mule Account Network Topologies', fontsize=14, fontweight='bold',
                 color=DARK, y=1.02)

    node_opts = dict(node_color='white', edgecolors=DARK, linewidths=2, node_size=700)
    edge_opts = dict(edge_color=MID, width=2, arrows=True, arrowsize=20,
                     connectionstyle='arc3,rad=0.1')
    label_opts = dict(font_size=8, font_weight='bold', font_color=DARK)

    # Star Pattern
    ax = axes[0]
    ax.set_title('Star Pattern\n(Aggregator / Distributor)', fontsize=11, fontweight='bold',
                 color=DARK, pad=10)
    G = nx.DiGraph()
    sources = ['S1', 'S2', 'S3', 'S4', 'S5']
    G.add_node('MULE', type='mule')
    G.add_node('OUT', type='out')
    for s in sources:
        G.add_node(s)
        G.add_edge(s, 'MULE')
    G.add_edge('MULE', 'OUT')
    pos = {}
    for i, s in enumerate(sources):
        angle = np.pi/2 + i * (2*np.pi/5)
        pos[s] = (np.cos(angle)*1.3, np.sin(angle)*1.3 + 0.2)
    pos['MULE'] = (0, 0.2)
    pos['OUT'] = (0, -1.5)

    colors = ['white' if n not in ['MULE'] else '#cccccc' for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=colors, edgecolors=DARK,
                           linewidths=2, node_size=700)
    nx.draw_networkx_edges(G, pos, ax=ax, **edge_opts)
    nx.draw_networkx_labels(G, pos, ax=ax, **label_opts)

    ax.text(0, -2.1, '5 inflows → 1 mule → 1 outflow\nScore: +45', ha='center',
            fontsize=8, color=LIGHT, style='italic')
    ax.axis('off')

    # Chain Pattern
    ax = axes[1]
    ax.set_title('Chain Pattern\n(Layered Laundering)', fontsize=11, fontweight='bold',
                 color=DARK, pad=10)
    G2 = nx.DiGraph()
    chain = ['A', 'B', 'C', 'D', 'E']
    for i in range(len(chain)-1):
        G2.add_edge(chain[i], chain[i+1])
    pos2 = {n: (i*1.2, -i*0.8) for i, n in enumerate(chain)}

    colors2 = ['#cccccc' if n in ['B','C','D'] else 'white' for n in G2.nodes()]
    nx.draw_networkx_nodes(G2, pos2, ax=ax, node_color=colors2, edgecolors=DARK,
                           linewidths=2, node_size=700)
    nx.draw_networkx_edges(G2, pos2, ax=ax, **edge_opts)
    nx.draw_networkx_labels(G2, pos2, ax=ax, **label_opts)

    ax.text(2.4, -3.8, 'Sequential A→B→C→D→E\n4+ hops: Score +20 to +35', ha='center',
            fontsize=8, color=LIGHT, style='italic')
    ax.axis('off')

    # Circular Pattern
    ax = axes[2]
    ax.set_title('Circular Pattern\n(Fund Rotation)', fontsize=11, fontweight='bold',
                 color=DARK, pad=10)
    G3 = nx.DiGraph()
    circle = ['A', 'B', 'C', 'D']
    for i in range(len(circle)):
        G3.add_edge(circle[i], circle[(i+1) % len(circle)])
    pos3 = {}
    for i, n in enumerate(circle):
        angle = np.pi/2 + i * (2*np.pi/4)
        pos3[n] = (np.cos(angle)*1.2, np.sin(angle)*1.2)

    nx.draw_networkx_nodes(G3, pos3, ax=ax, node_color='#cccccc', edgecolors=DARK,
                           linewidths=2, node_size=700)
    nx.draw_networkx_edges(G3, pos3, ax=ax, edge_color=MID, width=2, arrows=True,
                           arrowsize=20, connectionstyle='arc3,rad=0.15')
    nx.draw_networkx_labels(G3, pos3, ax=ax, **label_opts)

    ax.text(0, -1.9, 'Loop: A→B→C→D→A\nScore: +50', ha='center',
            fontsize=8, color=LIGHT, style='italic')
    ax.axis('off')

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '03_graph_patterns.png'))
    plt.close(fig)
    print("[+] 03_graph_patterns.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 4: Device Fingerprinting Flow
# ═══════════════════════════════════════════════════════════════════════
def diagram_device_flow():
    fig, ax = plt.subplots(1, 1, figsize=(12, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.5)
    ax.axis('off')
    ax.set_title('Device Fingerprinting Detection Flow', fontsize=14, fontweight='bold',
                 color=DARK, pad=15)

    # Left side: Device Concentration
    draw_box(ax, 0.3, 3.5, 2.5, 1.2, 'Device\nMapping', fontsize=10, bold=True, fill='#e0e0e0')
    draw_box(ax, 0.3, 1.5, 2.5, 1.5, 'Device D1\nused by:\nAcc1, Acc2,\nAcc3, Acc4, Acc5',
             fontsize=8, fill='#f0f0f0')
    draw_arrow(ax, 1.55, 3.5, 1.55, 3.05, lw=1.5)

    # Middle: Analysis
    draw_box(ax, 3.8, 3.5, 3.0, 1.2, 'Concentration\nAnalysis', fontsize=10, bold=True, fill='#d8d8d8')
    draw_arrow(ax, 2.8, 4.1, 3.8, 4.1, lw=1.5)

    draw_box(ax, 3.8, 1.8, 3.0, 1.2, 'Multi-Device\nRotation Check', fontsize=10, bold=True, fill='#d8d8d8')
    draw_arrow(ax, 2.8, 2.25, 3.8, 2.55, lw=1.5)

    # Scoring thresholds
    draw_box(ax, 7.8, 3.8, 3.8, 0.7, '10+ accounts → +50\n5+ accounts → +40\n3+ accounts → +30',
             fontsize=8, fill='#f0f0f0')
    draw_arrow(ax, 6.8, 4.1, 7.8, 4.15, lw=1.5)

    draw_box(ax, 7.8, 2.0, 3.8, 0.7, '5+ devices → +30\n3+ devices → +20',
             fontsize=8, fill='#f0f0f0')
    draw_arrow(ax, 6.8, 2.4, 7.8, 2.35, lw=1.5)

    # Output
    draw_box(ax, 4.5, 0.2, 4.0, 1.0, 'Device Risk Score\n(Weight: 15%)',
             fontsize=10, bold=True, fill='#cccccc')
    draw_arrow(ax, 5.3, 1.8, 5.5, 1.25, lw=1.5)
    draw_arrow(ax, 9.7, 2.0, 7.5, 1.0, lw=1.5)

    fig.savefig(os.path.join(OUT_DIR, '04_device_flow.png'))
    plt.close(fig)
    print("[+] 04_device_flow.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 5: Risk Scoring Pipeline
# ═══════════════════════════════════════════════════════════════════════
def diagram_risk_pipeline():
    fig, ax = plt.subplots(1, 1, figsize=(14, 6.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    ax.set_title('Risk Scoring Pipeline with Confidence Boosting', fontsize=14, fontweight='bold',
                 color=DARK, pad=15)

    # 5 signal modules at top
    signals = [
        ('Behavioral\n25%', 0.5),
        ('Graph\n40%', 3.0),
        ('Device\n15%', 5.5),
        ('Temporal\n10%', 8.0),
        ('ML\n10%', 10.5),
    ]
    for (name, x) in signals:
        draw_box(ax, x, 5.0, 2.2, 1.0, name, fontsize=9, bold=True, fill='#dcdcdc')
        draw_arrow(ax, x + 1.1, 5.0, x + 1.1, 4.45, lw=1.5)

    # Weighted Sum
    draw_box(ax, 2.5, 3.5, 8.0, 0.85, 'Weighted Sum:  R_base = 0.25·S_B + 0.40·S_G + 0.15·S_D + 0.10·S_T + 0.10·S_ML',
             fontsize=9, bold=True, fill='#e8e8e8')
    draw_arrow(ax, 6.5, 3.5, 6.5, 2.95, lw=2)

    # Confidence Boosting
    draw_box(ax, 1.5, 1.8, 10.5, 1.1, '', fill='#f0f0f0', lw=2)
    ax.text(6.75, 2.65, 'Confidence Boosting Layer', ha='center', va='center',
            fontsize=11, fontweight='bold', color=DARK)

    boost_items = ['4+ signals\n→ +20', '3 signals\n→ +15', '2 signals\n→ +8',
                   'Graph+Device\n→ +10', 'Beh+Graph\n→ +8']
    for i, item in enumerate(boost_items):
        x = 1.8 + i * 2.05
        draw_box(ax, x, 1.85, 1.8, 0.55, item, fontsize=7.5, fill='#e0e0e0')

    draw_arrow(ax, 6.5, 1.8, 6.5, 1.2, lw=2)

    # Classification output
    levels = [
        ('CRITICAL\n≥85', '#c0c0c0'),
        ('HIGH\n70-84', '#d0d0d0'),
        ('MEDIUM\n40-69', '#e0e0e0'),
        ('LOW\n<40', '#f0f0f0'),
    ]
    for i, (name, fill) in enumerate(levels):
        x = 2.0 + i * 2.6
        draw_box(ax, x, 0.2, 2.2, 0.85, name, fontsize=9, bold=True, fill=fill)

    ax.text(6.5, -0.1, 'Final Risk Classification (capped at 100)', ha='center',
            fontsize=9, color=LIGHT, style='italic')

    fig.savefig(os.path.join(OUT_DIR, '05_risk_pipeline.png'))
    plt.close(fig)
    print("[+] 05_risk_pipeline.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 6: Risk Distribution Chart
# ═══════════════════════════════════════════════════════════════════════
def diagram_risk_distribution():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Detection Results Overview', fontsize=14, fontweight='bold',
                 color=DARK, y=1.02)

    # Bar chart: Risk scores per mule scenario
    scenarios = ['Star\nAggregator', 'Circular\nNetwork', 'Chain\nLaundering',
                 'Device\nRing', 'Rapid\nOnboarding', 'Night\nSmurfing']
    scores = [92, 88, 76, 72, 95, 78]
    colors_bar = ['#333333' if s >= 85 else '#666666' if s >= 70 else '#999999' for s in scores]

    bars = ax1.barh(scenarios, scores, color=colors_bar, edgecolor=DARK, linewidth=1)
    ax1.set_xlim(0, 105)
    ax1.axvline(x=85, color=DARK, linestyle='--', linewidth=1, alpha=0.5)
    ax1.axvline(x=70, color=MID, linestyle='--', linewidth=1, alpha=0.4)
    ax1.axvline(x=40, color=LIGHT, linestyle='--', linewidth=1, alpha=0.3)

    ax1.text(87, 5.5, 'CRITICAL', fontsize=7, color=DARK, style='italic')
    ax1.text(72, 5.5, 'HIGH', fontsize=7, color=MID, style='italic')
    ax1.text(42, 5.5, 'MEDIUM', fontsize=7, color=LIGHT, style='italic')

    for bar, score in zip(bars, scores):
        ax1.text(score + 1, bar.get_y() + bar.get_height()/2,
                 str(score), va='center', fontsize=9, fontweight='bold', color=DARK)

    ax1.set_xlabel('Risk Score', fontsize=10, color=DARK)
    ax1.set_title('Mule Scenario Detection Scores', fontsize=11, fontweight='bold', color=DARK)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    # Pie chart: Risk distribution
    risk_counts = {'CRITICAL': 3, 'HIGH': 3, 'MEDIUM': 0, 'LOW': 25}
    labels = [f'{k}\n({v})' for k, v in risk_counts.items() if v > 0]
    sizes = [v for v in risk_counts.values() if v > 0]
    grays = ['#444444', '#777777', '#cccccc']

    wedges, texts, autotexts = ax2.pie(sizes, labels=labels, autopct='%1.0f%%',
                                        colors=grays, startangle=90,
                                        textprops={'fontsize': 9, 'color': DARK},
                                        wedgeprops={'edgecolor': DARK, 'linewidth': 1.5})
    for at in autotexts:
        at.set_fontweight('bold')
        at.set_fontsize(10)

    ax2.set_title('Overall Risk Distribution\n(6 mule + 25 legitimate)', fontsize=11,
                  fontweight='bold', color=DARK)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '06_risk_distribution.png'))
    plt.close(fig)
    print("[+] 06_risk_distribution.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 7: Deployment Architecture
# ═══════════════════════════════════════════════════════════════════════
def diagram_deployment():
    fig, ax = plt.subplots(1, 1, figsize=(13, 6))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 6)
    ax.axis('off')
    ax.set_title('Deployment Architecture (Prototype → Production)', fontsize=14,
                 fontweight='bold', color=DARK, pad=15)

    # Prototype side (left)
    draw_box(ax, 0.2, 0.2, 5.8, 5.5, '', fill='#f5f5f5', lw=2, border_color='#999999')
    ax.text(3.1, 5.4, 'PROTOTYPE (Current)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK)

    proto_items = [
        (0.5, 4.2, 'Docker Compose'),
        (0.5, 3.3, 'FastAPI + Uvicorn'),
        (0.5, 2.4, 'CSV Data Files'),
        (0.5, 1.5, 'NetworkX (in-memory)'),
        (0.5, 0.6, 'Pickle Model Store'),
    ]
    for (x, y, txt) in proto_items:
        draw_box(ax, x, y, 5.2, 0.7, txt, fontsize=9, fill='#e0e0e0')

    # Arrow in middle
    ax.annotate('', xy=(7.2, 3.0), xytext=(6.3, 3.0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=3))
    ax.text(6.75, 3.5, 'Scale Up', ha='center', fontsize=9, fontweight='bold', color=MID)

    # Production side (right)
    draw_box(ax, 7.2, 0.2, 5.5, 5.5, '', fill='#ebebeb', lw=2, border_color='#555555')
    ax.text(9.95, 5.4, 'PRODUCTION (Target)', ha='center', va='center',
            fontsize=12, fontweight='bold', color=DARK)

    prod_items = [
        (7.5, 4.2, 'Kubernetes + Auto-scaling'),
        (7.5, 3.3, 'API Gateway + Load Balancer'),
        (7.5, 2.4, 'Kafka + PostgreSQL'),
        (7.5, 1.5, 'Neo4j Graph Database'),
        (7.5, 0.6, 'MLflow Model Registry'),
    ]
    for (x, y, txt) in prod_items:
        draw_box(ax, x, y, 4.9, 0.7, txt, fontsize=9, bold=True, fill='#d0d0d0')

    # Arrows between corresponding items
    for i in range(5):
        y = proto_items[i][1] + 0.35
        ax.annotate('', xy=(7.5, y), xytext=(5.7, y),
                    arrowprops=dict(arrowstyle='->', color=LIGHT, lw=1, linestyle='--'))

    fig.savefig(os.path.join(OUT_DIR, '07_deployment.png'))
    plt.close(fig)
    print("[+] 07_deployment.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 8: Roadmap Timeline
# ═══════════════════════════════════════════════════════════════════════
def diagram_roadmap():
    fig, ax = plt.subplots(1, 1, figsize=(14, 5))
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 5)
    ax.axis('off')
    ax.set_title('MVP Roadmap: 16-Week Development Plan', fontsize=14, fontweight='bold',
                 color=DARK, pad=15)

    # Timeline bar
    ax.plot([1, 16], [2.8, 2.8], color=DARK, linewidth=3, solid_capstyle='round')

    # Phase markers
    phases = [
        (1, 4, 'Phase 1\nCore Infrastructure', 'Kafka ingestion\nPostgreSQL\nNeo4j\nRedis cache', '#e0e0e0'),
        (5, 8, 'Phase 2\nAdvanced Detection', 'GNN models\nIncremental learning\nMulti-hop device\nBidirectional analysis', '#d0d0d0'),
        (9, 12, 'Phase 3\nScale & Integration', 'Kubernetes\nUPI Switch plugin\nAlert management\nFeedback loop', '#c0c0c0'),
        (13, 16, 'Phase 4\nProduction Hardening', 'A/B testing\nSAR automation\nSOC 2 audit\nSub-10ms latency', '#b0b0b0'),
    ]

    for (start, end, title, details, fill) in phases:
        w = end - start + 0.8
        # Main phase bar
        draw_box(ax, start - 0.2, 3.2, w, 1.2, title, fontsize=9, bold=True, fill=fill)
        # Details below
        draw_box(ax, start - 0.2, 0.8, w, 1.8, details, fontsize=7.5, fill='#f0f0f0',
                 border_color='#aaaaaa')
        # Timeline dots
        ax.plot(start, 2.8, 'o', color=DARK, markersize=10, zorder=5)
        ax.plot(end, 2.8, 'o', color=MID, markersize=7, zorder=4)

    # Week labels
    for w in [1, 4, 5, 8, 9, 12, 13, 16]:
        ax.text(w, 2.4, f'W{w}', ha='center', va='top', fontsize=7, color=LIGHT)

    fig.savefig(os.path.join(OUT_DIR, '08_roadmap.png'))
    plt.close(fig)
    print("[+] 08_roadmap.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 9: Security Test Results Summary
# ═══════════════════════════════════════════════════════════════════════
def diagram_security():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={'width_ratios': [2, 1]})
    fig.suptitle('Security Testing Results: 42/42 Passed', fontsize=14, fontweight='bold',
                 color=DARK, y=1.02)

    # Bar chart
    categories = ['Auth', 'Injection', 'Rate\nLimit', 'CORS', 'Input\nValidation',
                  'HTTP\nMethods', 'Headers', 'Audit\nLog']
    tests = [6, 10, 3, 3, 7, 4, 5, 4]
    passed = [6, 10, 3, 3, 7, 4, 5, 4]

    x_pos = np.arange(len(categories))
    bars = ax1.bar(x_pos, tests, color='#cccccc', edgecolor=DARK, linewidth=1.2, label='Total')
    bars2 = ax1.bar(x_pos, passed, color='#666666', edgecolor=DARK, linewidth=1.2,
                    label='Passed', width=0.5)

    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(categories, fontsize=8)
    ax1.set_ylabel('Number of Tests', fontsize=10, color=DARK)
    ax1.set_title('Tests by Category', fontsize=11, fontweight='bold', color=DARK)
    ax1.legend(fontsize=8, frameon=True, edgecolor=LIGHT)
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    for bar, val in zip(bars, tests):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
                 str(val), ha='center', fontsize=8, fontweight='bold', color=DARK)

    # Donut chart
    ax2.pie([42], colors=['#555555'], startangle=90,
            wedgeprops={'width': 0.4, 'edgecolor': 'white', 'linewidth': 3})
    ax2.text(0, 0, '42/42\n100%', ha='center', va='center',
             fontsize=18, fontweight='bold', color=DARK)
    ax2.set_title('Overall Pass Rate', fontsize=11, fontweight='bold', color=DARK)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '09_security_results.png'))
    plt.close(fig)
    print("[+] 09_security_results.png")


# ═══════════════════════════════════════════════════════════════════════
# DIAGRAM 10: Ensemble Signal Contribution (Radar/Spider)
# ═══════════════════════════════════════════════════════════════════════
def diagram_signal_radar():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5.5),
                                    subplot_kw={'projection': 'polar'})
    fig.suptitle('Signal Contribution Analysis', fontsize=14, fontweight='bold',
                 color=DARK, y=1.02)

    labels = ['Behavioral', 'Graph\nAnalytics', 'Device\nFingerprint', 'Temporal', 'ML Anomaly']
    n = len(labels)
    angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
    angles += angles[:1]

    # Mule account (star aggregator) - high on most signals
    mule_scores = [75, 92, 50, 35, 68]
    mule_scores += mule_scores[:1]

    ax1.plot(angles, mule_scores, 'o-', color='#333333', linewidth=2, markersize=6)
    ax1.fill(angles, mule_scores, alpha=0.15, color='#333333')
    ax1.set_xticks(angles[:-1])
    ax1.set_xticklabels(labels, fontsize=8, color=DARK)
    ax1.set_ylim(0, 100)
    ax1.set_yticks([25, 50, 75, 100])
    ax1.set_yticklabels(['25', '50', '75', '100'], fontsize=7, color=LIGHT)
    ax1.set_title('Mule Account\n(Star Aggregator, Score: 92)', fontsize=10,
                  fontweight='bold', color=DARK, pad=20)
    ax1.grid(True, color='#cccccc', linewidth=0.5)

    # Legitimate account - low on all
    legit_scores = [12, 5, 0, 8, 15]
    legit_scores += legit_scores[:1]

    ax2.plot(angles, legit_scores, 'o-', color='#888888', linewidth=2, markersize=6)
    ax2.fill(angles, legit_scores, alpha=0.1, color='#888888')
    ax2.set_xticks(angles[:-1])
    ax2.set_xticklabels(labels, fontsize=8, color=DARK)
    ax2.set_ylim(0, 100)
    ax2.set_yticks([25, 50, 75, 100])
    ax2.set_yticklabels(['25', '50', '75', '100'], fontsize=7, color=LIGHT)
    ax2.set_title('Legitimate Account\n(Normal User, Score: 8)', fontsize=10,
                  fontweight='bold', color=DARK, pad=20)
    ax2.grid(True, color='#cccccc', linewidth=0.5)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, '10_signal_radar.png'))
    plt.close(fig)
    print("[+] 10_signal_radar.png")


# ═══════════════════════════════════════════════════════════════════════
# RUN ALL
# ═══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating FinGuard B/W diagrams...")
    print(f"Output directory: {OUT_DIR}\n")

    diagram_system_flow()
    diagram_architecture()
    diagram_graph_patterns()
    diagram_device_flow()
    diagram_risk_pipeline()
    diagram_risk_distribution()
    diagram_deployment()
    diagram_roadmap()
    diagram_security()
    diagram_signal_radar()

    print(f"\nDone! {10} diagrams generated in {OUT_DIR}")
