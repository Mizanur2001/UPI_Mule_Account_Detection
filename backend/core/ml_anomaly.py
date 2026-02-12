"""
ML-based Anomaly Detection Module for UPI Mule Account Detection.
Uses Isolation Forest (unsupervised) + statistical Z-score outlier detection 
to identify anomalous transaction behavior without requiring labeled training data.

This is a key innovation: works on zero labeled fraud data, making it 
deployable from day-one in any UPI ecosystem.
"""

import numpy as np
import pandas as pd
from collections import defaultdict


class IsolationForestLite:
    """
    Lightweight Isolation Forest implementation for anomaly detection.
    No scikit-learn dependency — pure NumPy for production portability.
    
    Theory: Anomalies are "few and different", so they are isolated 
    earlier in random binary trees. Normal points require more splits.
    """

    def __init__(self, n_trees: int = 100, max_samples: int = 256, random_state: int = 42):
        self.n_trees = n_trees
        self.max_samples = max_samples
        self.rng = np.random.RandomState(random_state)
        self.trees = []
        self._fitted = False

    def _build_tree(self, X: np.ndarray, depth: int = 0, max_depth: int = 10):
        n_samples, n_features = X.shape
        if n_samples <= 1 or depth >= max_depth:
            return {"type": "leaf", "size": n_samples}

        feature = self.rng.randint(0, n_features)
        min_val, max_val = X[:, feature].min(), X[:, feature].max()

        if min_val == max_val:
            return {"type": "leaf", "size": n_samples}

        split = self.rng.uniform(min_val, max_val)
        left_mask = X[:, feature] < split
        right_mask = ~left_mask

        return {
            "type": "split",
            "feature": feature,
            "split": split,
            "left": self._build_tree(X[left_mask], depth + 1, max_depth),
            "right": self._build_tree(X[right_mask], depth + 1, max_depth),
        }

    def fit(self, X: np.ndarray):
        """Fit the isolation forest on feature matrix X."""
        n = min(len(X), self.max_samples)
        max_depth = int(np.ceil(np.log2(max(n, 2))))

        self.trees = []
        for _ in range(self.n_trees):
            indices = self.rng.choice(len(X), size=n, replace=False) if len(X) > n else np.arange(len(X))
            tree = self._build_tree(X[indices], max_depth=max_depth)
            self.trees.append(tree)

        self._n_samples = n
        self._fitted = True
        return self

    def _path_length(self, x: np.ndarray, tree: dict, depth: int = 0) -> float:
        if tree["type"] == "leaf":
            return depth + self._c(tree["size"])
        if x[tree["feature"]] < tree["split"]:
            return self._path_length(x, tree["left"], depth + 1)
        return self._path_length(x, tree["right"], depth + 1)

    @staticmethod
    def _c(n: int) -> float:
        """Average path length of unsuccessful search in BST."""
        if n <= 1:
            return 0
        return 2.0 * (np.log(n - 1) + 0.5772156649) - 2.0 * (n - 1) / n

    def anomaly_score(self, X: np.ndarray) -> np.ndarray:
        """
        Compute anomaly scores. Higher = more anomalous (0 to 1 scale).
        """
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        scores = np.zeros(len(X))
        c_n = self._c(self._n_samples)

        for i, x in enumerate(X):
            avg_path = np.mean([self._path_length(x, tree) for tree in self.trees])
            scores[i] = 2 ** (-avg_path / c_n) if c_n > 0 else 0.5

        return scores


def extract_account_features(account_id: str, txns: pd.DataFrame,
                              accounts: pd.DataFrame, devices: pd.DataFrame) -> dict:
    """
    Extract feature vector for one account from transaction data.
    Features designed to capture mule-like behavioral signatures.
    """
    acc_txns = txns[(txns["sender"] == account_id) | (txns["receiver"] == account_id)]
    sent = txns[txns["sender"] == account_id]
    recv = txns[txns["receiver"] == account_id]

    total_txns = len(acc_txns)
    total_sent = len(sent)
    total_recv = len(recv)

    amount_sent = sent["amount"].sum() if total_sent > 0 else 0
    amount_recv = recv["amount"].sum() if total_recv > 0 else 0
    avg_amount = acc_txns["amount"].mean() if total_txns > 0 else 0
    max_amount = acc_txns["amount"].max() if total_txns > 0 else 0
    std_amount = acc_txns["amount"].std() if total_txns > 1 else 0

    # Unique counterparties
    unique_senders = recv["sender"].nunique() if total_recv > 0 else 0
    unique_receivers = sent["receiver"].nunique() if total_sent > 0 else 0

    # Pass-through ratio
    if amount_recv > 0:
        pass_through = amount_sent / amount_recv
    else:
        pass_through = 0 if amount_sent == 0 else 2.0

    # In/out degree ratio
    degree_ratio = unique_senders / max(unique_receivers, 1)

    # Account age
    acc_meta = accounts[accounts["account_id"] == account_id]
    age_days = acc_meta["account_age_days"].values[0] if len(acc_meta) > 0 else 365

    # Device count
    acc_devices = devices[devices["account_id"] == account_id]
    n_devices = acc_devices["device_id"].nunique() if len(acc_devices) > 0 else 0

    # Shared device accounts
    if len(acc_devices) > 0:
        device_ids = acc_devices["device_id"].unique()
        shared_accounts = devices[devices["device_id"].isin(device_ids)]["account_id"].nunique() - 1
    else:
        shared_accounts = 0

    return {
        "total_txns": total_txns,
        "total_sent": total_sent,
        "total_recv": total_recv,
        "amount_sent": amount_sent,
        "amount_recv": amount_recv,
        "avg_amount": avg_amount,
        "max_amount": max_amount,
        "std_amount": std_amount if not np.isnan(std_amount) else 0,
        "unique_senders": unique_senders,
        "unique_receivers": unique_receivers,
        "pass_through_ratio": min(pass_through, 5.0),
        "degree_ratio": min(degree_ratio, 10.0),
        "age_days": age_days,
        "n_devices": n_devices,
        "shared_device_accounts": shared_accounts,
        "txns_per_day": total_txns / max(age_days, 1),
        "volume_per_day": (amount_sent + amount_recv) / max(age_days, 1),
    }


def ml_anomaly_detection(account_ids: list, txns: pd.DataFrame,
                          accounts: pd.DataFrame, devices: pd.DataFrame) -> dict:
    """
    Run ML-based anomaly detection across all accounts.
    Returns dict {account_id: {"anomaly_score": float, "anomaly_label": str, "features": dict}}
    """
    # Extract features for all accounts
    feature_list = []
    valid_ids = []

    for acc_id in account_ids:
        feats = extract_account_features(acc_id, txns, accounts, devices)
        feature_list.append(feats)
        valid_ids.append(acc_id)

    if len(feature_list) == 0:
        return {}

    # Build feature matrix
    feature_names = list(feature_list[0].keys())
    X = np.array([[f[k] for k in feature_names] for f in feature_list], dtype=np.float64)

    # Normalize features (min-max scaling)
    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    X_range = X_max - X_min
    X_range[X_range == 0] = 1  # Avoid division by zero
    X_norm = (X - X_min) / X_range

    # Run Isolation Forest
    iforest = IsolationForestLite(n_trees=100, max_samples=min(256, len(X)))
    iforest.fit(X_norm)
    anomaly_scores = iforest.anomaly_score(X_norm)

    # Also compute Z-score based outlier detection
    z_scores = np.abs((X_norm - X_norm.mean(axis=0)) / (X_norm.std(axis=0) + 1e-10))
    z_anomaly = z_scores.mean(axis=1)
    z_normalized = (z_anomaly - z_anomaly.min()) / (z_anomaly.max() - z_anomaly.min() + 1e-10)

    # Ensemble: combine isolation forest + z-score
    ensemble_scores = 0.7 * anomaly_scores + 0.3 * z_normalized

    # Map to 0-100 scale
    min_e, max_e = ensemble_scores.min(), ensemble_scores.max()
    if max_e > min_e:
        scaled_scores = ((ensemble_scores - min_e) / (max_e - min_e)) * 100
    else:
        scaled_scores = np.full_like(ensemble_scores, 50)

    results = {}
    for i, acc_id in enumerate(valid_ids):
        score_val = float(scaled_scores[i])
        if score_val >= 70:
            label = "ANOMALOUS"
        elif score_val >= 45:
            label = "SUSPICIOUS"
        else:
            label = "NORMAL"

        results[acc_id] = {
            "anomaly_score": round(score_val, 1),
            "anomaly_label": label,
            "isolation_score": round(float(anomaly_scores[i]) * 100, 1),
            "zscore_score": round(float(z_normalized[i]) * 100, 1),
            "features": feature_list[i],
        }

    return results
