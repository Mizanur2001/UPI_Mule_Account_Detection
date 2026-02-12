#!/usr/bin/env python
"""Quick verification that enhanced system works"""

print("Testing enhanced UPI mule detection system...")

try:
    print("\n1. Testing imports...")
    from dashboard.enhanced_dashboard import *
    print("   ✅ Dashboard modules OK")
    
    from backend.api.score import batch_score_accounts
    print("   ✅ Score functions OK")
    
    from backend.core.behavioral import behavioral_risk
    from backend.core.graph_analysis import build_transaction_graph
    from backend.core.device_risk import device_risk
    print("   ✅ Detection modules OK")
    
    print("\n2. Testing data loading...")
    from backend.utils.data_loader import load_transactions, load_accounts, load_devices
    txns = load_transactions()
    accounts = load_accounts()
    devices = load_devices()
    print(f"   ✅ Data loaded: {len(txns)} txns, {len(accounts)} accounts, {len(devices)} devices")
    
    print("\n3. Testing graph construction...")
    G = build_transaction_graph(txns)
    print(f"   ✅ Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    
    print("\n4. Testing batch scoring (sample)...")
    sample_accs = list(G.nodes())[:5]
    results = batch_score_accounts(sample_accs, txns, accounts, devices, G)
    print(f"   ✅ Scoring working: {len(results)} accounts scored")
    
    print("\n5. Checking for mule accounts...")
    high_risk = [acc for acc, result in results.items() if result["risk_level"] == "HIGH"]
    print(f"   ✅ Found {len(high_risk)} HIGH risk accounts in sample")
    for acc in high_risk[:3]:
        print(f"      - {acc}: {results[acc]['risk_score']}/100")
        for reason in results[acc]['reasons'][:2]:
            print(f"        • {reason}")
    
    print("\n" + "="*60)
    print("✅ ALL SYSTEMS OPERATIONAL - Ready for dashboard!")
    print("="*60)
    print("\nRun: python -m streamlit run dashboard/enhanced_dashboard.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
