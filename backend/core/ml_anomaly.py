
import os
import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from collections import defaultdict

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "isolation_forest.pkl")
META_PATH = os.path.join(MODEL_DIR, "model_meta.json")


class IsolationForestLite:

    def __init__(self, n_trees: int = 100, max_samples: int = 256, random_state: int = 42):
        self.n_trees = n_trees
        self.max_samples = max_samples
        self.rng = np.random.RandomState(random_state)
        self.trees = []
        self._fitted = False

    # Recursively partitions data into an isolation tree
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

    # Trains the forest by building isolation trees
    def fit(self, X: np.ndarray):
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
        if n <= 1:
            return 0
        return 2.0 * (np.log(n - 1) + 0.5772156649) - 2.0 * (n - 1) / n

    # Computes anomaly scores via average path lengths
    def anomaly_score(self, X: np.ndarray) -> np.ndarray:
        if not self._fitted:
            raise RuntimeError("Must call fit() first")

        scores = np.zeros(len(X))
        c_n = self._c(self._n_samples)

        for i, x in enumerate(X):
            avg_path = np.mean([self._path_length(x, tree) for tree in self.trees])
            scores[i] = 2 ** (-avg_path / c_n) if c_n > 0 else 0.5

        return scores

    def save(self, path: str):
        with open(path, "wb") as f:
            pickle.dump({
                "trees": self.trees,
                "n_samples": self._n_samples,
                "n_trees": self.n_trees,
                "max_samples": self.max_samples,
                "fitted": self._fitted,
            }, f)

    @classmethod
    def load(cls, path: str) -> "IsolationForestLite":
        with open(path, "rb") as f:
            data = pickle.load(f)
        model = cls(n_trees=data["n_trees"], max_samples=data["max_samples"])
        model.trees = data["trees"]
        model._n_samples = data["n_samples"]
        model._fitted = data["fitted"]
        return model


# Permutation-based feature importance for anomaly detection
def compute_feature_importance(model: IsolationForestLite, X: np.ndarray,
                                feature_names: list) -> dict:
    baseline_scores = model.anomaly_score(X)
    importance = {}

    rng = np.random.RandomState(42)
    for i, name in enumerate(feature_names):
        X_perm = X.copy()
        X_perm[:, i] = rng.permutation(X_perm[:, i])
        perm_scores = model.anomaly_score(X_perm)
        importance[name] = round(float(np.mean(np.abs(baseline_scores - perm_scores))), 4)

    total = sum(importance.values()) or 1
    importance = {k: round(v / total * 100, 1) for k, v in importance.items()}
    return dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))


# Explains which features drive an account's anomaly score
def explain_account(model: IsolationForestLite, X: np.ndarray,
                     account_idx: int, feature_names: list) -> list:
    baseline = float(model.anomaly_score(X[account_idx:account_idx+1])[0])
    contributions = []

    rng = np.random.RandomState(42)
    for i, name in enumerate(feature_names):
        X_mod = X[account_idx:account_idx+1].copy()
        X_mod[0, i] = np.median(X[:, i])
        modified_score = float(model.anomaly_score(X_mod)[0])
        delta = baseline - modified_score
        contributions.append({
            "feature": name,
            "contribution": round(delta * 100, 2),
            "direction": "increases risk" if delta > 0 else "decreases risk",
        })

    contributions.sort(key=lambda x: abs(x["contribution"]), reverse=True)
    return contributions[:5]


# Extracts 17 ML features for a single account
def extract_account_features(account_id: str, txns: pd.DataFrame,
                              accounts: pd.DataFrame, devices: pd.DataFrame) -> dict:
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

    unique_senders = recv["sender"].nunique() if total_recv > 0 else 0
    unique_receivers = sent["receiver"].nunique() if total_sent > 0 else 0

    if amount_recv > 0:
        pass_through = amount_sent / amount_recv
    else:
        pass_through = 0 if amount_sent == 0 else 2.0

    degree_ratio = unique_senders / max(unique_receivers, 1)

    acc_meta = accounts[accounts["account_id"] == account_id]
    age_days = acc_meta["account_age_days"].values[0] if len(acc_meta) > 0 else 365

    acc_devices = devices[devices["account_id"] == account_id]
    n_devices = acc_devices["device_id"].nunique() if len(acc_devices) > 0 else 0

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


# Runs full ML pipeline: features, train/load, score, explain
def ml_anomaly_detection(account_ids: list, txns: pd.DataFrame,
                          accounts: pd.DataFrame, devices: pd.DataFrame,
                          force_retrain: bool = False) -> dict:
    feature_list = []
    valid_ids = []

    for acc_id in account_ids:
        feats = extract_account_features(acc_id, txns, accounts, devices)
        feature_list.append(feats)
        valid_ids.append(acc_id)

    if len(feature_list) == 0:
        return {}

    feature_names = list(feature_list[0].keys())
    X = np.array([[f[k] for k in feature_names] for f in feature_list], dtype=np.float64)

    X_min = X.min(axis=0)
    X_max = X.max(axis=0)
    X_range = X_max - X_min
    X_range[X_range == 0] = 1
    X_norm = (X - X_min) / X_range

    iforest = None
    if not force_retrain and os.path.exists(MODEL_PATH):
        try:
            iforest = IsolationForestLite.load(MODEL_PATH)
        except Exception:
            iforest = None

    if iforest is None:
        iforest = IsolationForestLite(n_trees=100, max_samples=min(256, len(X)))
        iforest.fit(X_norm)
        iforest.save(MODEL_PATH)
        meta = {
            "trained_at": datetime.utcnow().isoformat() + "Z",
            "n_accounts": len(valid_ids),
            "n_features": len(feature_names),
            "feature_names": feature_names,
            "n_trees": iforest.n_trees,
        }
        with open(META_PATH, "w") as f:
            json.dump(meta, f, indent=2)

    anomaly_scores = iforest.anomaly_score(X_norm)

    feat_importance = compute_feature_importance(iforest, X_norm, feature_names)

    z_scores = np.abs((X_norm - X_norm.mean(axis=0)) / (X_norm.std(axis=0) + 1e-10))
    z_anomaly = z_scores.mean(axis=1)
    z_normalized = (z_anomaly - z_anomaly.min()) / (z_anomaly.max() - z_anomaly.min() + 1e-10)

    ensemble_scores = 0.7 * anomaly_scores + 0.3 * z_normalized

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

        explanations = explain_account(iforest, X_norm, i, feature_names)

        results[acc_id] = {
            "anomaly_score": round(score_val, 1),
            "anomaly_label": label,
            "isolation_score": round(float(anomaly_scores[i]) * 100, 1),
            "zscore_score": round(float(z_normalized[i]) * 100, 1),
            "features": feature_list[i],
            "explanations": explanations,
            "feature_importance": feat_importance,
        }

    return results
