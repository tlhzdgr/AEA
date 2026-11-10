# Codebook: processed data

The five files in this folder are written by the analysis scripts from the anonymized raw exports in `data/raw/`
(see `data/raw/README.md`). Running `run_all.ps1` recreates them.

| File | Written by | One row is | Rows |
|---|---|---|---|
| `trials_all.csv` | `analysis/01_data_processing.Rmd` | one main trial of one lab, online or AEA respondent | 44,064 (153 × 288) |
| `respondent_summary.csv` | `analysis/01_data_processing.Rmd` | one lab, online or AEA respondent | 153 |
| `respondent_qc.csv` | `analysis/01_data_processing.Rmd` | one lab, online or AEA respondent | 153 |
| `sample_flow.csv` | `analysis/01_data_processing.Rmd` | one sample | 3 |
| `agea_trials.csv` | `analysis/04_agea_data_processing.Rmd` | one main trial of one AGEA respondent | 14,688 (51 × 288) |

## Common conventions

- **Samples:** `Lab` = human participants tested in the lab and verified in person (Utrecht University, April to May
  2026); `Online` = participants recruited through Prolific and tested remotely (April to May 2026; the 51 respondents
  drawn at random from 54, seed 19); `AEA` = sessions completed by the artificial experiment agent (April to May 2026);
  `AGEA` = sessions completed by the artificial general experiment agent (October 2026; Supplemental Material, Table S5).
  In the lab, at least one student researcher was present throughout each session; online sessions were unsupervised.
- **Respondent:** one lab or online participant, or one task completion by an agent.
- **Trials:** only the 288 main trials (96 congruent, 96 neutral, 96 incongruent). Practice trials, instructions,
  breaks and Gorilla's logging rows are removed. No trials are excluded and response times are not trimmed.
- **Response times** are in milliseconds, measured by Gorilla from stimulus onset. The response deadline was 2,000 ms.
- **Task accuracy** is the proportion of correct responses over all 288 trials, with misses counted as incorrect.
  Response time measures use correct responses only (`rt_valid == TRUE`).
- **IDs are pseudonyms.** `ID` and `ex_ID` are order-preserving codes: the i-th smallest original value gets the i-th
  code, so codes keep the sort order of the original IDs (which the seeded analyses depend on). The mapping to the
  original IDs is not kept. `ID` codes are assigned across all three samples together, so their ranges interleave.
- **Missing values** are empty cells (`NA`). They occur only where a measure is undefined (see the notes below).

## `trials_all.csv`

| Column | Type | Description |
|---|---|---|
| `sample` | text | `Lab`, `Online` or `AEA` |
| `ex_ID` | text | Pseudonym of Gorilla's `Participant Public ID` (`X0001` to `X0153`) |
| `ID` | integer | Pseudonym of Gorilla's `Participant Private ID` (1001 to 1153); the respondent key used in all analyses |
| `trial_number` | integer | Position of the trial among the 288 main trials (1 to 288) |
| `display` | text | Gorilla display name; always `Trials` |
| `congruency` | text | `congruent` (word matches ink color), `neutral` (word is XXXX) or `incongruent` (word differs from ink color) |
| `stimulus` | text | Stimulus as stored in the Gorilla spreadsheet: HTML with the ink color as a hex code and the word in bold, e.g. `<span style="color:#0000FF;"><strong>RED</strong></span>` is RED in blue ink (`#FF0000` red, `#008000` green, `#0000FF` blue, `#FFFF00` yellow) |
| `response` | text | Key response as recorded by Gorilla: `red`, `green`, `blue`, `yellow` (keys R, G, B, Y), or `missed` (no response within 2,000 ms) |
| `rt` | number (ms) | Response time. For missed trials, Gorilla's logged time of the timeout event; it is not a response time and is never analyzed |
| `correct` | 0/1 | 1 if the response matched the ink color; misses are coded 0 |
| `missed` | TRUE/FALSE | TRUE if no response was given within 2,000 ms |
| `rt_valid` | TRUE/FALSE | TRUE for correct, non-missed trials; only these enter response time measures |

## `respondent_summary.csv`

| Column | Type | Description |
|---|---|---|
| `sample`, `ID`, `ex_ID` | | As in `trials_all.csv` |
| `n_trials` | integer | Number of main trials; always 288 |
| `accuracy` | proportion | Task accuracy over all 288 trials (misses count as incorrect) |
| `mean_rt` | ms | Mean correct response time over all conditions |
| `n_missed` | integer | Number of missed trials |
| `prop_miss` | proportion | `n_missed` / 288 |
| `n_keys` | integer | Number of different response keys used (misses not counted) |
| `accuracy_congruent`, `accuracy_neutral`, `accuracy_incongruent` | proportion | Task accuracy within each condition (96 trials each) |
| `mean_rt_congruent`, `mean_rt_neutral`, `mean_rt_incongruent` | ms | Mean correct response time within each condition; empty if the condition has no correct response |
| `congruency_effect` | ms | `mean_rt_incongruent` − `mean_rt_congruent`; used in quality check 4 and Figure 2b |
| `facilitation` | ms | `mean_rt_neutral` − `mean_rt_congruent`; classifier feature |
| `interference` | ms | `mean_rt_incongruent` − `mean_rt_neutral`; classifier feature |

Note: `congruency_effect` (incongruent − congruent) and `interference` (incongruent − neutral) are different measures.
One online respondent had no correct incongruent response, so `mean_rt_incongruent`, `congruency_effect` and
`interference` are empty for that respondent; it could not be classified by the SVMs.

The other six classifier features (response time SD, skewness, drift, lag-one autocorrelation, and so on) are not stored
here; `analysis/03_classification.ipynb` computes them from `trials_all.csv`.

## `respondent_qc.csv`

The six quality checks of the Method (*Conventional Quality Checks*). A flag marks a respondent a researcher would
usually exclude; no respondent was removed.

| Column | Type | Description |
|---|---|---|
| `sample`, `ID`, `ex_ID`, `accuracy`, `mean_rt`, `n_missed`, `prop_miss`, `n_keys`, `congruency_effect` | | As in `respondent_summary.csv` |
| `rt_cong`, `rt_incong` | ms | Same as `mean_rt_congruent` and `mean_rt_incongruent` |
| `rt_sample_mean`, `rt_sample_sd` | ms | Mean and SD of `mean_rt` within the respondent's own sample |
| `rt_z` | z | (`mean_rt` − `rt_sample_mean`) / `rt_sample_sd` |
| `flag_accuracy` | TRUE/FALSE | Check 1: `accuracy` < .80 |
| `flag_fast_rt` | TRUE/FALSE | Check 2: `mean_rt` < 300 ms |
| `flag_rt_3sd` | TRUE/FALSE | Check 3: \|`rt_z`\| > 3 |
| `flag_no_congruency` | TRUE/FALSE | Check 4: `rt_incong` ≤ `rt_cong`, or either is empty |
| `flag_missed` | TRUE/FALSE | Check 5: `prop_miss` > .10 |
| `flag_invariant` | TRUE/FALSE | Check 6: `n_keys` < 4 |
| `flag_any` | TRUE/FALSE | TRUE if any of the six flags is TRUE |

## `sample_flow.csv`

| Column | Type | Description |
|---|---|---|
| `sample` | text | `Lab`, `Online` or `AEA` |
| `respondents_in_export` | integer | Respondents in the raw export |
| `with_experimental_trials` | integer | Respondents with at least one main-trial response |
| `analyzed` | integer | Respondents analyzed (51 per sample) |
| `not_analyzed_no_trials` | integer | Respondents without main-trial responses |
| `not_analyzed_draw` | integer | Online respondents not selected in the random draw of 51 of 54 |

## `agea_trials.csv`

Same coding rules as `trials_all.csv`. Used only for the generalization test (Supplemental Material, Table S5).

| Column | Type | Description |
|---|---|---|
| `sample` | text | Always `AGEA` |
| `ID` | text | `AGEA_001` to `AGEA_051`; the prefix keeps these IDs apart from the integer IDs of the other samples |
| `orig_ID` | integer | Order-preserving pseudonym of Gorilla's `Participant Private ID` (1 to 51); `ID` is built from it |
| `ex_ID` | text | Pseudonym of Gorilla's `Participant Public ID`; one value (`AGEAX001`) because all sessions ran under one public ID |
| `source_file` | text | Raw file the row came from (`raw_agea.csv`) |
| `trial_number`, `display`, `congruency`, `response`, `rt`, `correct`, `missed`, `rt_valid` | | As in `trials_all.csv` |
| `stimulus` | text | Gorilla stimulus ID in the form `WORD_inkcolor`, e.g. `GREEN_blue` is GREEN in blue ink; `XXXX_red` is a neutral trial in red ink |
