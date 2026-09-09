
from __future__ import annotations
import numpy as np
from scipy.interpolate import interp1d

PATTERN_NAMES = [
    "Head & Shoulders",
    "Inverse Head & Shoulders",
    "Double Top",
    "Double Bottom",
    "Cup & Handle",
    "Ascending Triangle",
    "Descending Triangle",
    "Rising Wedge",
    "Falling Wedge",
]

def _resample(arr, n=60):
    x = np.asarray(arr, dtype=float)
    if len(x) == 0:
        return np.zeros(n)
    if len(x) == 1:
        return np.repeat(x[0], n)
    old = np.linspace(0, 1, len(x))
    new = np.linspace(0, 1, n)
    return interp1d(old, x, kind="linear")(new)

def normalize_shape(arr, n=60):
    x = _resample(arr, n)
    x = x - np.mean(x)
    sd = float(np.std(x))
    if sd > 1e-12:
        x = x / sd
    return x

def _anchor_curve(points, n=60):
    xp = np.linspace(0, 1, len(points))
    x = np.linspace(0, 1, n)
    return np.interp(x, xp, np.asarray(points, float))

def base_templates(n=60):
    # Idealized normalized reference shapes. They are used as pattern-recognition
    # templates, not claimed to be market examples.
    curves = {
        "Head & Shoulders": [0.0, 0.65, 0.15, 1.0, 0.2, 0.68, 0.05],
        "Inverse Head & Shoulders": [0.0, -0.65, -0.15, -1.0, -0.2, -0.68, -0.05],
        "Double Top": [0.0, 0.85, 0.25, 0.83, 0.05],
        "Double Bottom": [0.0, -0.85, -0.25, -0.83, -0.05],
        "Cup & Handle": [0.72, 0.25, -0.55, -0.82, -0.45, 0.1, 0.72, 0.48, 0.68],
        "Ascending Triangle": [0.0, 0.75, 0.2, 0.76, 0.38, 0.75, 0.55, 0.77],
        "Descending Triangle": [0.0, -0.75, -0.2, -0.76, -0.38, -0.75, -0.55, -0.77],
        "Rising Wedge": [0.0, 0.45, 0.15, 0.7, 0.42, 0.87, 0.68],
        "Falling Wedge": [0.0, -0.45, -0.15, -0.7, -0.42, -0.87, -0.68],
    }
    return {name: normalize_shape(_anchor_curve(points, n), n) for name, points in curves.items()}

def build_reference_bank(n=60, copies_per_class=12, seed=42):
    rng = np.random.default_rng(seed)
    bases = base_templates(n)
    X, y = [], []
    for name, base in bases.items():
        X.append(base)
        y.append(name)
        for _ in range(copies_per_class - 1):
            noise = rng.normal(0, 0.08, n)
            drift = np.linspace(0, rng.normal(0, 0.12), n)
            X.append(normalize_shape(base + noise + drift, n))
            y.append(name)
    return np.vstack(X), np.asarray(y)

def classify_shape(arr, n=60, k=5):
    x = normalize_shape(arr, n)
    X, y = build_reference_bank(n=n)
    dists = np.mean((X - x[None, :]) ** 2, axis=1)
    idx = np.argsort(dists)[:max(1, min(k, len(dists)))]
    labels = y[idx]
    unique, counts = np.unique(labels, return_counts=True)
    winner = unique[np.argmax(counts)]
    vote = float(np.max(counts) / len(idx))
    same = idx[labels == winner]
    mean_dist = float(np.mean(dists[same])) if len(same) else float(np.mean(dists[idx]))
    similarity = float(np.exp(-mean_dist))
    return {
        "predicted_pattern": str(winner),
        "knn_vote": vote,
        "template_similarity": similarity,
        "mean_distance": mean_dist,
        "neighbors": [{"pattern": str(y[i]), "distance": float(dists[i])} for i in idx],
    }

def score_detection(df, detection):
    s = max(0, int(detection.get("start_idx", 0)))
    e = min(len(df) - 1, int(detection.get("end_idx", len(df) - 1)))
    if e - s < 5:
        return {**detection, "match_score": float(detection.get("confidence", 0.0))}
    rec = classify_shape(df["close"].iloc[s:e+1].to_numpy())
    geom = float(detection.get("confidence", 0.0))
    label_agreement = 1.0 if rec["predicted_pattern"] == detection.get("pattern") else 0.45
    combined = 0.55 * geom + 0.30 * rec["template_similarity"] + 0.15 * (rec["knn_vote"] * label_agreement)
    out = dict(detection)
    out["recognition"] = rec
    out["match_score"] = float(max(0.0, min(1.0, combined)))
    return out
