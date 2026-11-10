# REFORMS checklist

Completed REFORMS checklist (Kapoor et al., 2024, *Science Advances*, https://doi.org/10.1126/sciadv.adk3452) for *A "Human-Like" Stroop Effect No Longer Implies a Human Participant*. The same checklist is Table S6 of the Supplemental Material. "Where reported" refers to the manuscript, the Supplemental Material, or this repository.

## Module 1: Study goals

| Item | Where reported | How it is addressed |
|---|---|---|
| 1a. Population of the claim | Introduction (last paragraph); Discussion | Online behavioral experiments: agent vs. human data; one task, platform, and two agents |
| 1b. Motivation for the population | Introduction (paragraphs 1–5) | Wide use of online recruitment; LLM agents complete online studies |
| 1c. Motivation for ML | Method: Detection With SVMs | Combines features; covers human-only and labeled-agent cases |

## Module 2: Computational reproducibility

| Item | Where reported | How it is addressed |
|---|---|---|
| 2a. Data | Transparency Statement; README | Raw (metadata removed) and processed data in repository **[DOI to be added]** |
| 2b. Code | Transparency Statement; Method | Analysis code in repository **[release, DOI to be added]**; AEA prompts on request only |
| 2c. Computing infrastructure | Method; README | R 4.5.2, Python 3.12, scikit-learn 1.7; Windows 11 laptop (Intel Core i7, 16 GB RAM) |
| 2d. README | README | Software, run instructions, script per table and figure |
| 2e. Reproduction script | README | One script rebuilds all tables and figures, fixed seeds |

## Module 3: Data quality

| Item | Where reported | How it is addressed |
|---|---|---|
| 3a. Sources, timing, ground truth | Method: Samples, Procedure; Supplement | April–May 2026 (AGEA: October 2026); labels from data collection; online sample unlabeled |
| 3b. Sampling frame | Method: Samples | Lab: university students; online: Prolific, 51 of 54 drawn; AEA: 51 respondents |
| 3c. Suitability of the data | Introduction; Method: Samples | Identical task copies; known labels |
| 3d. Outcome variable | Method: Models; Table S3 | Sample membership (lab vs. AEA); classified as AEA = flagged |
| 3e. Sample size, outcome frequencies | Method: Samples, Classifier Evaluation | 51 per sample; splits of 25 + 25 training, 26 + 26 test |
| 3f. Missing data | Results: Exclusion Criteria; Table 3 | No respondent missed > 10% of trials; one online respondent unclassifiable |
| 3g. Representativeness | Discussion: limitations | Lab sample as human reference; online setting differs |

## Module 4: Data preprocessing

| Item | Where reported | How it is addressed |
|---|---|---|
| 4a. Exclusions | Method: Samples, Data Processing | None; online respondents drawn before any check |
| 4b. Impossible or corrupt data | Method: Data Processing | Non-responses coded as misses; no trimming |
| 4c. Transformations | Method: Data Processing, Features; README | Trial coding, features, training-set standardization |

## Module 5: Modeling

| Item | Where reported | How it is addressed |
|---|---|---|
| 5a. Models | Method: Models | One-class SVM (RBF, ν = .08); supervised SVM (RBF, C = 1) |
| 5b. Justification of model types | Method: Detection With SVMs | One model per situation (human-only vs. labeled agent data) |
| 5c. Evaluation | Method: Classifier Evaluation; Table S2 | 5,000 stratified Monte Carlo splits; 10-fold and leave-one-out as checks |
| 5d. Model selection | Method: Features, Models | Settings fixed; one feature per property from a larger candidate set |
| 5e. Hyperparameter tuning | Method: Models; Tables S1, S4 | None; ν varied (Table S1); thresholds set on training data |
| 5f. Baselines | Results; Tables 1, S3 | Quality checks; chance (.50); single-feature AUCs |

## Module 6: Data leakage

| Item | Where reported | How it is addressed |
|---|---|---|
| 6a. Training data only | Method: Classifier Evaluation | Standardization and thresholds from training data only |
| 6b. Train–test dependencies | Introduction (last paragraph); Method: Artificial Experiment Agent, Classifier Evaluation; Table S5 | Split by respondent; each AEA run is one respondent, because the agent modeled human response times and accuracy; a second agent was tested separately |
| 6c. Legitimate features | Method: Features | Trial data only; no metadata |

## Module 7: Metrics and uncertainty

| Item | Where reported | How it is addressed |
|---|---|---|
| 7a. Metrics | Method: Classifier Evaluation, Positive Predictive Value | Sensitivity, specificity, accuracy; PPV at assumed rates |
| 7b. Uncertainty | Tables 2–4, S5 | Percentiles across splits; Wilson CIs; PPV percentiles (Table 4 note) |
| 7c. Statistical tests | – | None used |

## Module 8: Generalizability and limitations

| Item | Where reported | How it is addressed |
|---|---|---|
| 8a. External validity | Results; Tables 3, S5 | Second agent; online sample |
| 8b. Limits | Discussion: limitations | One task, platform, and two agents; unverified online sample; summary features |
