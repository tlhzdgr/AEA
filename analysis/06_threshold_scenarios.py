"""06 · Table S4: the supervised SVM with stricter decision thresholds and class weights for lower contamination rates.

Supplemental Material, *Stricter Decision Thresholds and Class Weights*; Results, *Positive Predictive Value*
("More cautious settings ... reduced false alarms, on average, only by missing more AEA respondents").
Reads outputs/tables/respondent_features.csv (from 03). Writes to outputs/tables/:
    table_S4_splits.csv        one row per split and setting (the 5,000 splits of 03)
    table_S4.csv               mean sensitivity and specificity per setting and PPV = s*pi / (s*pi + (1 - c)*(1 - pi))
                               for assumed contamination rates pi of 5, 10 and 20%, with the means s and c
Run from analysis/:  python 06_threshold_scenarios.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

F = ["rt_mean", "rt_sd", "rt_skew", "acc_mean", "rt_drift", "rt_autocorr", "interference", "facilitation"]
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "tables"
N = 5000
PIS = (0.05, 0.10, 0.20)

feat = pd.read_csv(OUT / "respondent_features.csv")
feat = feat[feat["sample"].isin(["Lab", "AEA"])].dropna(subset=F).reset_index(drop=True)
LAB = np.array(sorted(feat.ID[feat["sample"] == "Lab"])); AEA = np.array(sorted(feat.ID[feat["sample"] == "AEA"]))
X_all = feat.set_index("ID")[F]; y_all = feat.set_index("ID")["sample"].map({"AEA": 1, "Lab": 0})


def split(seed):                                   # the splits of 03
    r = np.random.default_rng(seed); lab = r.choice(LAB, len(LAB), replace=False); aea = r.choice(AEA, len(AEA), replace=False)
    lt = r.choice(lab, len(lab) // 2, replace=False); at = r.choice(aea, len(aea) // 2, replace=False)
    return np.concatenate([lt, at]), np.concatenate([np.setdiff1d(lab, lt), np.setdiff1d(aea, at)])


def metr(y, flag):
    tp = ((y == 1) & flag).sum(); fn = ((y == 1) & ~flag).sum(); fp = ((y == 0) & flag).sum(); tn = ((y == 0) & ~flag).sum()
    return tp / (tp + fn), tn / (tn + fp)


rows = []
for i in range(N):
    tr, te = split(1000 + i)
    sc = StandardScaler().fit(X_all.loc[tr]); Xtr = sc.transform(X_all.loc[tr]); Xte = sc.transform(X_all.loc[te])
    ytr = y_all.loc[tr].to_numpy(); yte = y_all.loc[te].to_numpy()
    svm = SVC(kernel="rbf", class_weight="balanced", random_state=42).fit(Xtr, np.where(ytr == 1, -1, 1))   # AEA = -1
    s_te = -svm.decision_function(Xte)            # higher = more AEA-like
    se, sp = metr(yte, svm.predict(Xte) == -1); rows.append(dict(split=i, scenario="Default (balanced, threshold 0)", sens=se, spec=sp))
    # Thresholds from 5-fold cross-validated scores within the training data; each inner fold has its own scaler.
    inner = np.zeros(len(ytr)); skf = StratifiedKFold(5, shuffle=True, random_state=i); Xraw = X_all.loc[tr].to_numpy()
    for a, b in skf.split(Xraw, ytr):
        isc = StandardScaler().fit(Xraw[a])
        m = SVC(kernel="rbf", class_weight="balanced", random_state=42).fit(isc.transform(Xraw[a]), np.where(ytr[a] == 1, -1, 1))
        inner[b] = -m.decision_function(isc.transform(Xraw[b]))
    for target in (0.95, 0.99):
        thr = np.quantile(inner[ytr == 0], target)   # 95th or 99th percentile of the lab training scores
        se, sp = metr(yte, s_te > thr); rows.append(dict(split=i, scenario=f"Threshold for {int(target*100)}% specificity", sens=se, spec=sp))
    for pi in PIS:
        w = {-1: pi / 0.5, 1: (1 - pi) / 0.5}        # class weights proportional to the assumed contamination rate
        m = SVC(kernel="rbf", class_weight=w, random_state=42).fit(Xtr, np.where(ytr == 1, -1, 1))
        se, sp = metr(yte, m.predict(Xte) == -1); rows.append(dict(split=i, scenario=f"Weights for {int(pi*100)}% prevalence", sens=se, spec=sp, pi=pi))
pd.DataFrame(rows).to_csv(OUT / "table_S4_splits.csv", index=False)

# ---- Table S4: means across splits, settings ordered as in the supplement ----
d = pd.read_csv(OUT / "table_S4_splits.csv")
weights = d[d["scenario"].str.startswith("Weights")].drop_duplicates("scenario").sort_values("pi", ascending=False)["scenario"].tolist()
order = [x for x in d["scenario"].unique() if not x.startswith("Weights")] + weights
rows = []
for scenario in order:
    g = d[d["scenario"] == scenario]
    s, c = g["sens"].mean(), g["spec"].mean()
    r = {"scenario": scenario, "sens_mean": s, "spec_mean": c, "sens_med": g["sens"].median(), "spec_med": g["spec"].median()}
    for pi in PIS:
        k = int(round(pi * 100))
        hits, fa = s * pi, (1 - c) * (1 - pi)
        r[f"ppv{k}"] = hits / (hits + fa)
    rows.append(r)
summary = pd.DataFrame(rows)
summary.to_csv(OUT / "table_S4.csv", index=False)

# Table S4 reports these means; it omits the PPV where mean specificity is 1 (no lab respondent flagged in any split).
print(summary[["scenario", "sens_mean", "spec_mean", "ppv5", "ppv10", "ppv20"]].round(3).to_string(index=False))
