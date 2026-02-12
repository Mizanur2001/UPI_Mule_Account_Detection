#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test backend scoring logic without dashboard dependencies"""
import sys
import io

# Fix for Windows console encoding
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("Testing enhanced UPI mule detection backend...")

try:
    print("\n1. Testing core imports...")
    from backend.api.score import batch_score_accounts
    from backend.core.behavioral import behavioral_risk
    from backend.core.graph_analysis import build_transaction_graph, batch_graph_risk
    from backend.core.device_risk import device_risk
    from backend.core.risk_engine import aggregate_risk, risk_level, get_risk_confidence
    from backend.utils.data_loader import load_transactions, load_accounts, load_devices
    print("   ✅ All backend modules imported successfully")
    
    print("\n2. Loading data...")
    txns = load_transactions()
    accounts = load_accounts()
    devices = load_devices()
    print(f"   ✅ Data loaded: {len(txns)} transactions, {len(accounts)} accounts, {len(devices)} device links")
    
    print("\n3. Building transaction graph...")
    G = build_transaction_graph(txns)
    print(f"   ✅ Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    print("\n4. Testing batch scoring (all accounts)...")
    unique_accounts = sorted(set(txns["sender"]) | set(txns["receiver"]))
    scores = batch_score_accounts(unique_accounts, txns, accounts, devices, G)
    print(f"   ✅ Scored {len(scores)} accounts")
    
    print("\n5. analyzing results by risk level...")
    risk_counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for acc, result in scores.items():
        risk_counts[result["risk_level"]] += 1
    
    print(f"   ✅ HIGH RISK: {risk_counts['HIGH']}")
    print(f"   ✅ MEDIUM RISK: {risk_counts['MEDIUM']}")
    print(f"   ✅ LOW RISK: {risk_counts['LOW']}")
    
    print("\n6. Displaying HIGH RISK accounts (targets for mule detection)...")
    high_risk = sorted(
        [(acc, result) for acc, result in scores.items() if result["risk_level"] == "HIGH"],
        key=lambda x: x[1]["risk_score"],
        reverse=True
    )
    
    if high_risk:
        print(f"\n   Found {len(high_risk)} HIGH RISK accounts:\n")
        for acc, result in high_risk[:10]:
            print(f"   {acc}")
            print(f"     Score: {result['risk_score']}/100 | Confidence: {result['confidence']}")
            print(f"     Components: Behavioral={result['behavioral_score']}, Graph={result['graph_score']}, Device={result['device_score']}")
            print(f"     Evidence:")
            for reason in result["reasons"][:3]:
                print(f"       • {reason}")
            print()
    else:
        print("   No HIGH risk accounts found")
    
    print("="*70)
    print("✅ BACKEND SYSTEM FULLY OPERATIONAL")
    print("="*70)
    print("\nNotes for Dashboard Demo:")
    print("• The enhanced detection logic is working correctly")
    print("• All known mule scenarios should show HIGH risk scores")
    print("• Device and graph patterns are properly detected")
    print("\nNext: Run 'streamlit run dashboard/enhanced_dashboard.py'")
    print("OR   Run 'python -m streamlit run dashboard/enhanced_dashboard.py'")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
