"""
Core scoring logic for UPI Mule Account Detection.
Combines multiple risk factors into a comprehensive account score.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import logging

from backend.utils.data_loader import load_transactions, load_accounts, load_devices
from backend.core.behavioral import behavioral_risk
from backend.core.graph_analysis import build_transaction_graph, graph_risk, batch_graph_risk
from backend.core.device_risk import device_risk
from backend.core.temporal_analysis import temporal_risk
from backend.core.ml_anomaly import ml_anomaly_detection
from backend.core.risk_engine import aggregate_risk, risk_level, get_risk_confidence, get_recommended_action
from backend.utils.logger import get_logger

logger = get_logger("score")


def score_account(
    account_id: str,
    txns: Optional[pd.DataFrame] = None,
    accounts: Optional[pd.DataFrame] = None,
    devices: Optional[pd.DataFrame] = None,
    G: Optional[Any] = None,
    cycles: Optional[List] = None,
    _graph_cache: Optional[Dict[str, Tuple]] = None,
    _ml_cache: Optional[Dict[str, Dict]] = None,
) -> Dict[str, Any]:
    """
    Score a single account for mule risk.
    
    Args:
        account_id: The account to score
        txns: DataFrame of transactions
        accounts: DataFrame of account metadata
        devices: DataFrame of device information
        G: Precomputed transaction graph (networkx)
        cycles: Precomputed cycles for graph analysis
        _graph_cache: Cache of graph risk scores
        _ml_cache: Cache of ML anomaly scores
        
    Returns:
        Dictionary with comprehensive risk assessment
    """
    try:
        if txns is None:
            txns = load_transactions()
        if accounts is None:
            accounts = load_accounts()
        if devices is None:
            devices = load_devices()

        # Filter transactions for this account
        account_txns = txns[(txns["sender"] == account_id) | (txns["receiver"] == account_id)]

        # Handle missing account metadata safely
        account_meta_rows = accounts[accounts["account_id"] == account_id]
        if not account_meta_rows.empty:
            account_meta = account_meta_rows.iloc[0]
            behavioral_score, b_reasons = behavioral_risk(account_txns, account_meta)
        else:
            behavioral_score, b_reasons = 0, ["Account metadata not found"]
            logger.debug(f"No metadata found for account {account_id}")

        if G is None:
            G = build_transaction_graph(txns)

        # Use batch cache if provided (avoids re-running expensive graph algos)
        if _graph_cache is not None and account_id in _graph_cache:
            graph_score, g_reasons = _graph_cache[account_id]
        else:
            graph_score, g_reasons = graph_risk(account_id, G, precomputed_cycles=cycles)

        device_score, d_reasons = device_risk(account_id, devices)

        # Temporal analysis
        temporal_score, t_reasons = temporal_risk(account_id, account_txns)

        # ML anomaly score
        ml_score: float = 0.0
        ml_label: str = "N/A"
        if _ml_cache is not None and account_id in _ml_cache:
            ml_data = _ml_cache[account_id]
            ml_score = ml_data["anomaly_score"]
            ml_label = ml_data["anomaly_label"]

        final_score = aggregate_risk(behavioral_score, graph_score, device_score,
                                      temporal_score, ml_score)
        risk_lvl = risk_level(final_score)
        confidence = get_risk_confidence(final_score)
        action = get_recommended_action(risk_lvl)

        result = {
            "account_id": account_id,
            "risk_score": final_score,
            "risk_level": risk_lvl,
            "confidence": confidence,
            "recommended_action": action,
            "behavioral_score": int(behavioral_score),
            "graph_score": int(graph_score),
            "device_score": int(device_score),
            "temporal_score": int(temporal_score),
            "ml_anomaly_score": round(ml_score, 1),
            "ml_anomaly_label": ml_label,
            "reasons": b_reasons + g_reasons + d_reasons + t_reasons,
            "signal_count": sum([
                behavioral_score >= 25,
                graph_score >= 25,
                device_score >= 15,
                temporal_score >= 20,
                ml_score >= 40,
            ]),
        }
        
        logger.debug(f"Account {account_id} scored: risk={final_score}, level={risk_lvl}")
        return result
        
    except Exception as e:
        logger.error(f"Error scoring account {account_id}: {e}")
        raise


def batch_score_accounts(
    account_ids: List[str],
    txns: pd.DataFrame,
    accounts: pd.DataFrame,
    devices: pd.DataFrame,
    G: Any
) -> Dict[str, Dict[str, Any]]:
    """
    Score multiple accounts efficiently in one pass.
    Graph analysis runs ONCE for the entire graph, then each account
    just does a dict lookup. ML anomaly detection also runs batch-wide.
    
    Args:
        account_ids: List of account IDs to score
        txns: DataFrame of transactions
        accounts: DataFrame of account metadata
        devices: DataFrame of device information
        G: Transaction graph (networkx)
        
    Returns:
        Dictionary mapping account_id to score result dict
    """
    try:
        logger.info(f"Starting batch score for {len(account_ids)} accounts")
        
        # Pre-compute all expensive operations once
        graph_cache = batch_graph_risk(G)
        logger.debug(f"Graph risk cache computed for {len(graph_cache)} accounts")

        # Run ML anomaly detection in batch (Isolation Forest + Z-score)
        ml_cache = ml_anomaly_detection(list(account_ids), txns, accounts, devices)
        logger.debug(f"ML cache computed for {len(ml_cache)} accounts")

        results: Dict[str, Dict[str, Any]] = {}
        for acc in account_ids:
            results[acc] = score_account(
                acc,
                txns=txns,
                accounts=accounts,
                devices=devices,
                G=G,
                _graph_cache=graph_cache,
                _ml_cache=ml_cache,
            )
        
        logger.info(f"Batch score completed for {len(results)} accounts")
        return results
        
    except Exception as e:
        logger.error(f"Error in batch score: {e}")
        raise

