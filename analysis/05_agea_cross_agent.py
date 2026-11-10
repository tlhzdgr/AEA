"""05 · Table S5: does a supervised SVM trained on one agent detect the other?

Supplemental Material, *Generalization to a Second Agent*; Results, *Generalization to a Second Agent*.
Reads data/processed/trials_all.csv (lab, AEA) and agea_trials.csv (from 04), and outputs/tables/respondent_features.csv
(from 03, to check the features and to keep its row order). Writes to outputs/tables/:
    agea_features.csv            the 8 features of the lab, AEA and AGEA respondents
    table_S5_splits.csv          one row per split
    table_S5.csv                 Table S5 (medians [2.5th, 97.5th percentiles]); the AUC column supports the text
                                 "Both SVMs still gave the other agent's respondents higher scores than lab respondents"
    table_S5_loss.csv            splits in which balanced accuracy fell, or was tied, for the other agent
Per split (seeds 1000 to 5999): 25 lab + 25 agent respondents train, 26 held-out lab, AEA and AGEA respondents test.
    A: supervised SVM lab vs AEA (as in 03) -> tested on AEA (same agent) and AGEA (other agent)
    B: supervised SVM lab vs AGEA           -> tested on AGEA (same agent) and AEA (other agent)
The lab and AEA splits equal the splits of 03 (same draw order); AGEA has its own random stream.
Run from analysis/:  python 05_agea_cross_agent.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

ROOT = Path(__file__).resolve().parents[1]
PROC, OUT = ROOT / "data" / "processed", ROOT / "outputs" / "tables"
OUT.mkdir(parents=True, exist_ok=True)
F8 = ["rt_mean", "rt_sd", "rt_skew", "acc_mean", "rt_drift", "rt_autocorr", "interference", "facilitation"]


def nlz(x):
    s = f"{x:.2f}"
    return s.replace("0.", ".", 1) if s.startswith(("0.", "-0.")) else s


# ---- features: same function as 03 ----
def engineer_features(df):
    records = []
    for pid, p in df.groupby("ID"):
        p = p.sort_values("trial_number")
        resp = p[~p["missed"]]
        rt = resp["rt"].to_numpy(float)
        if len(rt) < 10:
            continue
        ac = pd.Series(rt).autocorr(lag=1)
        c = resp[resp["correct"] == 1].groupby("congruency")["rt"].mean()
        records.append({"ID": pid, "sample": p["sample"].iloc[0],
                        "rt_mean": rt.mean(), "rt_sd": rt.std(), "rt_skew": float(pd.Series(rt).skew()),
                        "acc_mean": float(np.nanmean(p["correct"].to_numpy(float))),
                        "rt_drift": float(stats.linregress(resp["trial_number"].to_numpy(float), rt).slope),
                        "rt_autocorr": 0.0 if pd.isna(ac) else float(ac),
                        "interference": c.get("incongruent", np.nan) - c.get("neutral", np.nan),
                        "facilitation": c.get("neutral", np.nan) - c.get("congruent", np.nan)})
    return pd.DataFrame(records)


cols = ["sample", "ID", "trial_number", "congruency", "response", "rt", "correct", "missed", "rt_valid"]
main = pd.read_csv(PROC / "trials_all.csv", dtype={"ID": str})
main = main[main["sample"].isin(["Lab", "AEA"])]
agea = pd.read_csv(PROC / "agea_trials.csv", dtype={"ID": str})
assert set(main["ID"]).isdisjoint(agea["ID"])
trials = pd.concat([main[cols], agea[cols]], ignore_index=True)
trials["missed"] = trials["missed"].astype(bool)
features = engineer_features(trials)
features.to_csv(OUT / "agea_features.csv", index=False)
features = pd.read_csv(OUT / "agea_features.csv", dtype={"ID": str})   # the models use the values as saved

ref = pd.read_csv(OUT / "respondent_features.csv", dtype={"ID": str})          # written by 03
mm = features[features["sample"].isin(["Lab", "AEA"])].merge(ref[["ID"] + F8], on="ID", suffixes=("", "_03"))
assert len(mm) == 102 and all(np.allclose(mm[f], mm[f + "_03"], rtol=0, atol=1e-9, equal_nan=True) for f in F8)

# ---- respondents in the row order of 03 ----
f = features.dropna(subset=F8)
ORDER = ref["ID"].tolist()
f = pd.concat([f.set_index("ID").loc[[i for i in ORDER if i in set(f["ID"])]].reset_index(), f[f["sample"] == "AGEA"]],
              ignore_index=True)
G = {s: f[f["sample"] == s].sort_values("ID").reset_index(drop=True) for s in ("Lab", "AEA", "AGEA")}
assert [len(G[s]) for s in ("Lab", "AEA", "AGEA")] == [51, 51, 51]


def split3(seed):
    rng = np.random.default_rng(seed)
    out = {}
    perm = {s: rng.choice(np.array(G[s]["ID"]), 51, replace=False) for s in ("Lab", "AEA")}   # draw order of 03:
    for s in ("Lab", "AEA"):                       # permutation lab, permutation AEA, 25 lab, 25 AEA
        out[s] = rng.choice(perm[s], 25, replace=False), perm[s]
    rng2 = np.random.default_rng(seed + 100000)    # AGEA has its own stream, so lab and AEA stay identical to 03
    ids = rng2.choice(np.array(G["AGEA"]["ID"]), 51, replace=False)
    out["AGEA"] = rng2.choice(ids, 25, replace=False), ids
    return {s: (tr, G[s].set_index("ID").loc[np.setdiff1d(ids, tr), F8].to_numpy()) for s, (tr, ids) in out.items()}


def train_matrix(ids_lab, ids_agent):
    """Training rows in the row order of 03 (libsvm can depend on row order)."""
    d = f[f["ID"].isin(np.r_[ids_lab, ids_agent])]
    return d[F8].to_numpy(), np.where(d["sample"] == "Lab", 1.0, -1.0)


def auc(pos, neg, sv, sc):                          # higher score = more agent-like (agent = class -1)
    s = -np.r_[sv.decision_function(sc.transform(pos)), sv.decision_function(sc.transform(neg))]
    return roc_auc_score(np.r_[np.ones(len(pos)), np.zeros(len(neg))], s)


rows = []
for i in range(5000):
    d = split3(1000 + i)
    labtr, labte = d["Lab"]
    r = {"split": i}
    for name, agent in (("A_lab_vs_AEA", "AEA"), ("B_lab_vs_AGEA", "AGEA")):
        other = "AGEA" if agent == "AEA" else "AEA"
        X, y = train_matrix(labtr, d[agent][0])
        sc = StandardScaler().fit(X)
        sv = SVC(kernel="rbf", class_weight="balanced", random_state=42).fit(sc.transform(X), y)
        flag = lambda Z: float((sv.predict(sc.transform(Z)) == -1).mean())
        r[f"{name}_spec"] = 1 - flag(labte)
        r[f"{name}_sens_within"] = flag(d[agent][1])
        r[f"{name}_sens_cross"] = flag(d[other][1])
        r[f"{name}_auc_within"] = auc(d[agent][1], labte, sv, sc)
        r[f"{name}_auc_cross"] = auc(d[other][1], labte, sv, sc)
    rows.append(r)
S = pd.DataFrame(rows)
for n in ("A_lab_vs_AEA", "B_lab_vs_AGEA"):
    for k in ("within", "cross"):
        S[f"{n}_balacc_{k}"] = (S[f"{n}_spec"] + S[f"{n}_sens_{k}"]) / 2
S.to_csv(OUT / "table_S5_splits.csv", index=False)

# ---- Table S5 ----
q = lambda c: f"{nlz(S[c].median())} [{nlz(S[c].quantile(.025))}, {nlz(S[c].quantile(.975))}]"
T = [("Lab vs. AEA", "AEA (same agent)", "A_lab_vs_AEA", "within"),
     ("Lab vs. AEA", "AGEA (other agent)", "A_lab_vs_AEA", "cross"),
     ("Lab vs. AGEA", "AGEA (same agent)", "B_lab_vs_AGEA", "within"),
     ("Lab vs. AGEA", "AEA (other agent)", "B_lab_vs_AGEA", "cross")]
tab = pd.DataFrame([{"trained_on": a, "tested_on": b, "lab_specificity": q(f"{n}_spec"), "agent_detected": q(f"{n}_sens_{k}"),
                     "balanced_accuracy": q(f"{n}_balacc_{k}"), "AUC": q(f"{n}_auc_{k}")} for a, b, n, k in T])
tab.to_csv(OUT / "table_S5.csv", index=False)

# "It fell in every split, except for one split in which the two balanced accuracies ... were tied."
loss = pd.DataFrame([{"trained_on": n, "splits": len(S),
                      "fell": int((S[f"{n}_balacc_within"] > S[f"{n}_balacc_cross"]).sum()),
                      "tied": int((S[f"{n}_balacc_within"] == S[f"{n}_balacc_cross"]).sum()),
                      "rose": int((S[f"{n}_balacc_within"] < S[f"{n}_balacc_cross"]).sum())} for n in ("A_lab_vs_AEA", "B_lab_vs_AGEA")])
loss.to_csv(OUT / "table_S5_loss.csv", index=False)
print(tab.to_string(index=False)); print(loss.to_string(index=False))
