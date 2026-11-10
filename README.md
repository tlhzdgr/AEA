# A "Human-Like" Stroop Effect No Longer Implies a Human Participant

Data and analysis code for the article *A "Human-Like" Stroop Effect No Longer Implies a Human Participant* and its
Supplemental Material. The manuscript and the Supplemental Material are available as a preprint: **[link to be added]**.
Every table and figure in them is rebuilt from `data/raw/` by `run_all.ps1`.

## Overview

Three samples of 51 respondents each completed the same color-word Stroop task in Gorilla: a lab sample of human
participants verified in person, an online sample recruited through Prolific (51 of 54 drawn at random), and an
artificial experiment agent (AEA). We asked whether conventional quality checks, visual inspection and support vector
machines (SVMs) identify the AEA respondents. A second agent, the artificial general experiment agent (AGEA, 51
respondents), tests whether the supervised SVM detects an agent it was not trained on (Table S5).

## Key Findings

- All 51 AEA respondents showed the congruency effect (at least 113 ms) and passed all six common quality checks; visual inspection did not single them out either (Table 1, Figure 2)
- A one-class SVM trained only on verified human data performed poorly: median accuracy .63 (sensitivity .88, specificity .38), at chance in some splits (Table 2)
- A supervised SVM trained on labeled human and agent data reached a median accuracy of .94 (sensitivity .96, specificity .88) (Table 2)
- At an assumed 5% contamination rate, only about 3 in 10 of the supervised SVM's flags would be agents (PPV = .30) (Table 4)
- The supervised SVM did not generalize to a second agent it was not trained on: balanced accuracy dropped from .94 to .54 (Table S5)
- In the online sample, neither SVM flagged more respondents than expected from false alarms alone (Table 3)

## Repository structure

```
.
├── README.md
├── run_all.ps1                       rebuilds all tables and figures from data/raw/
├── requirements.txt                  Python and R package versions
├── REFORMS_checklist.md              completed REFORMS checklist (also Table S6 of the Supplemental Material)
├── data/
│   ├── raw/                          anonymized Gorilla exports, Stroop task only (see data/raw/README.md)
│   └── processed/                    trial- and respondent-level files written by analysis/01 and 04 (see CODEBOOK.md)
└── analysis/                         run in numerical order from inside analysis/
    ├── 00_anonymize_raw.py           original exports -> data/raw (needs the original exports, which are not shared)
    ├── 01_data_processing.Rmd        Method: samples, task structure, data processing, quality-check flags
    ├── 02_quality_and_visual.Rmd     Table 1, Figure 2
    ├── 03_classification.ipynb       Tables 2 to 4, Figure 3, Tables S1 to S3
    ├── 04_agea_data_processing.Rmd   AGEA sample
    ├── 05_agea_cross_agent.py        Table S5
    └── 06_threshold_scenarios.py     Table S4
```

Running the analyses rewrites `data/processed/` and writes `outputs/` (not stored in the repository): `outputs/tables/` (CSV
files), `outputs/figures/` and `outputs/reports/` (one HTML report per R Markdown file and notebook,
code with its output).

## From manuscript item to code

| Manuscript item | Code | Output (`outputs/tables/` unless noted) |
|---|---|---|
| Method, *Samples*; *Task and Design*; *Data Processing and Analysis* | `01` | `data/processed/sample_flow.csv`, `trials_all.csv`, `respondent_summary.csv`; `task_structure_check.csv` |
| Method, *Conventional Quality Checks* | `01` | `data/processed/respondent_qc.csv` |
| Table 1; Results, *Exclusion Criteria* | `02` | `table1_qc_flags.csv`, `exclusion_criteria_margins.csv` |
| Figure 2 and its footnote; Results, *Visual Inspection* | `02` | `outputs/figures/fig2.pdf`, `fig2_answer_key.csv`, `visual_inspection_support.csv` |
| Method, *Features* | `03` | `respondent_features.csv` |
| Table 2, Figure 3; Results, *Performance on Lab and AEA Data* | `03` | `mc_splits_all.csv`, `mc_summary.csv`, `fig3_counts.csv`, `outputs/figures/fig3.pdf` |
| Table 3; Results, *Application to the Online Sample* | `03` | `online_application.csv`, `online_agreement.csv`, `online_expected_false_alarms.csv`, `online_scores.csv` |
| Table 4; Results, *Positive Predictive Value* | `03` | `ppv_by_contamination.csv` |
| Tables S1 and S2 (robustness) | `03` | `robustness_nu.csv`, `robustness_cv.csv` |
| Table S3 (single features) | `03` | `feature_auc.csv`, `feature_descriptives.csv` |
| Table S4 (thresholds and class weights) | `06` | `table_S4.csv`, `table_S4_splits.csv` |
| Table S5; Results, *Generalization to a Second Agent* | `04`, `05` | `table_S5.csv`, `table_S5_splits.csv`, `table_S5_loss.csv` |

Figure 1 (task schematic) is a drawing and is not generated from data.

## Reproduce

Requirements: R 4.5 and Pandoc (packages in `requirements.txt`) and Python 3.12 (`pip install -r requirements.txt`).

```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

This knits the R Markdown files and executes the notebook and scripts (the 5,000-split analyses take several minutes; a full
run takes about 15 minutes on a laptop). Each file also runs on its own, in numerical order, from inside `analysis/`:

```powershell
cd analysis
Rscript -e "rmarkdown::render('01_data_processing.Rmd', output_dir = '../outputs/reports')"
python -m jupyter nbconvert --to html --execute --output-dir ../outputs/reports 03_classification.ipynb
python 05_agea_cross_agent.py
```

## Data

`data/raw/` holds the Gorilla exports of the Stroop task, anonymized by `analysis/00_anonymize_raw.py`: external IDs
(Prolific IDs, lab codes, agent labels) are replaced by order-preserving codes, and timestamps, time zone, completion and
session codes and device information are removed (details in `data/raw/README.md`). There are no questionnaire or
demographic data. `data/processed/` holds the files below, written by `analysis/01` and `04`; their respondent IDs are
order-preserving codes. They are included so that analyses 02 to 06 can be run without first running the R processing steps.
Every column is described in [`data/processed/CODEBOOK.md`](data/processed/CODEBOOK.md).

| File (`data/processed/`) | Unit | Content |
|---|---|---|
| `trials_all.csv` | trial | The 288 main trials of the 153 lab, online and AEA respondents, including incorrect responses and misses |
| `respondent_summary.csv` | respondent | Task accuracy, mean correct response time, misses, keys used, condition means, congruency effect, facilitation, interference |
| `respondent_qc.csv` | respondent | Quality-check measures and the six flags |
| `sample_flow.csv` | sample | Respondents in each raw export and in the analysis |
| `agea_trials.csv` | trial | The 51 AGEA respondents, same layout as `trials_all.csv` |

## Materials

The Stroop task (Gorilla Experiment Builder) is openly available on Gorilla Open Materials:
https://app.gorilla.sc/openmaterials/1372430

## Authors

- Talha Özüdoğru, Christian P. Janssen, Christoph Strauch, Leendert Van Maanen: Experimental Psychology & Helmholtz Institute, Utrecht University
- Silja Renooij: Department of Information and Computing Sciences, Utrecht University

## Citation

If you use these data or code, please cite the paper:

> Özüdoğru, T., Janssen, C. P., Renooij, S., Strauch, C., & Van Maanen, L. (2026). A "human-like" Stroop effect no longer implies a human participant. *Preprint.*

Funding: Dutch Railways (NS), the Dutch Research Council (NWO; grant KICH3.LTP.20.006) and the Dutch Ministry of Economic Affairs (EZ). Ethical approval: Ethics Review Board of the Faculty of Social and Behavioural Sciences, Utrecht University (reference 26-0757).

## License

The code and data in this repository are released under the [Creative Commons Attribution 4.0 International License (CC BY 4.0)](LICENSE): reuse is free for any purpose if you credit the authors (see Citation).
