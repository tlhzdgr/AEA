"""00 · Anonymize the raw Gorilla exports (Method, Samples; Research Transparency Statement, Data).

Reads the original exports, which are not shared (default folder: ../raw_original next to the repository; or pass
the folder as the first argument), and writes the shared raw files to data/raw/:

    raw_lab.csv     lab sample      (Gorilla experiment 267618 v3)
    raw_online.csv  online sample   (Gorilla experiment 272028 v3; 54 respondents, 51 analyzed)
    raw_aea.csv     AEA sample      (Gorilla experiment 268937 v2)
    raw_agea.csv    AGEA sample     (Gorilla experiment 290516 v1; Table S5)

What changes: the external IDs (Prolific IDs, lab codes, agent labels) in `Participant Public ID` are replaced by
codes P0001, P0002, ... that keep the sort order of the original IDs across the lab, online and AEA files; columns that
identify a respondent or their device or location are dropped (see DROP). Everything else, including Gorilla's
internal `Participant Private ID` and the row order, is unchanged, so analysis/01 and 04 give the same results from the
shared files as from the originals. The ID mapping is not saved. All four exports contain only the Stroop task.
Run from analysis/:  python 00_anonymize_raw.py [folder with the original exports]
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "raw_original"
OUT = ROOT / "data" / "raw"

FILES = {  # shared name: original export
    "raw_lab.csv":    "lab_data_exp_267618-v3_tasks.csv",
    "raw_online.csv": "data_exp_272028-v3_task-vcn4.csv",
    "raw_aea.csv":    "bot_data_exp_268937-v2_task-vcn4.csv",
    "raw_agea.csv":   "data_exp_290516-v1_task-vcn4.csv",
}
DROP = ["UTC Timestamp", "UTC Date and Time", "Local Timestamp", "Local Timezone", "Local Date and Time",
        "Schedule ID", "Participant Completion Code", "Participant External Session ID",
        "Participant Device Type", "Participant Device", "Participant OS", "Participant Browser",
        "Participant Monitor Size", "Participant Viewport Size"]
PUBLIC = "Participant Public ID"

# Read every cell as text, so that the shared files keep the exact values of the originals.
raw = {new: pd.read_csv(SRC / old, dtype=str, keep_default_na=False) for new, old in FILES.items()}
for new, d in raw.items():
    assert d["Task Name"].isin(["", *[t for t in d["Task Name"].unique() if "Stroop" in t]]).all(), f"{new}: non-Stroop rows"

# One code per external ID, in byte order of the original IDs over the lab, online and AEA files together
# (analysis/01 pseudonymizes these three samples jointly); the AGEA file is coded on its own (analysis/04).
def codes(ids):
    return {v: f"P{i:04d}" for i, v in enumerate(sorted(set(ids) - {""}), start=1)}

main = codes(pd.concat([raw[f][PUBLIC] for f in ("raw_lab.csv", "raw_online.csv", "raw_aea.csv")]))
agea = codes(raw["raw_agea.csv"][PUBLIC])

OUT.mkdir(parents=True, exist_ok=True)
for new, d in raw.items():
    m = agea if new == "raw_agea.csv" else main
    d[PUBLIC] = d[PUBLIC].map(lambda v: m.get(v, v))           # "" (Gorilla's END OF FILE row) stays empty
    d = d.drop(columns=[c for c in DROP if c in d.columns])
    d.to_csv(OUT / new, index=False)
    print(f"{new}: {len(d)} rows, {d[PUBLIC].replace('', pd.NA).nunique()} external IDs coded, {d.shape[1]} columns")
