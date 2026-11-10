# Raw data

Anonymized Gorilla exports of the Stroop task, written by `analysis/00_anonymize_raw.py` from the original exports
(not shared). Each file contains only the Stroop task; there are no questionnaire or demographic data.

| File | Sample | Respondents | Gorilla experiment |
|---|---|---|---|
| `raw_lab.csv` | lab sample (human participants verified in person) | 51 | 267618 v3 |
| `raw_online.csv` | online sample (Prolific; 51 of 54 drawn at random in `analysis/01`) | 54 | 272028 v3 |
| `raw_aea.csv` | artificial experiment agent (AEA) | 51 | 268937 v2 |
| `raw_agea.csv` | artificial general experiment agent (AGEA; Table S5) | 51 | 290516 v1 |

**Changed from the original exports:**
- `Participant Public ID` (Prolific IDs, lab codes, agent labels) is replaced by codes `P0001`, `P0002`, ... that keep the
  sort order of the original IDs; the mapping is not saved.
- Removed columns: `UTC Timestamp`, `UTC Date and Time`, `Local Timestamp`, `Local Timezone`, `Local Date and Time`,
  `Schedule ID`, `Participant Completion Code`, `Participant External Session ID`, `Participant Device Type`,
  `Participant Device`, `Participant OS`, `Participant Browser`, `Participant Monitor Size`, `Participant Viewport Size`.
- Unchanged: Gorilla's internal `Participant Private ID`, all task columns and the row order. `analysis/01` and `04`
  therefore give the same results from these files as from the original exports.

**Columns.** The files keep Gorilla's standard export format; Gorilla's documentation describes every column. The
analysis (`analysis/01` and `04`) uses only these:

| Column | Meaning |
|---|---|
| `Participant Public ID` | Respondent code (pseudonymized, see above) |
| `Participant Private ID` | Gorilla's internal respondent number |
| `Task Name` | Task; only the Stroop task is in these files |
| `Display` | Screen type; `Trials` = main trials, `Practice` = practice trials (others are instructions and breaks) |
| `Trial Number` | Trial position within the display |
| `Response Type` | Kind of row; only `response` rows (the key press or timeout) are analyzed |
| `Response` | `red`, `green`, `blue`, `yellow`, or `missed` (no response within 2,000 ms) |
| `Reaction Time` | Response time in ms from stimulus onset |
| `Correct` | 1 if the response matched the ink color (a miss is rescored as incorrect in the analysis) |
| `Spreadsheet: Congruency` | `congruent`, `neutral` or `incongruent` |
| `Spreadsheet: Stimulus_text` | Stimulus as HTML (word and ink color); used for the lab, online and AEA files |
| `Spreadsheet: Stimulus_ID` | Stimulus as `WORD_inkcolor`; used for the AGEA file |

The processed files derived from these exports are described in `data/processed/CODEBOOK.md`.

SHA-256 of the original exports used for the reported numbers:

| Original export | SHA-256 |
|---|---|
| `lab_data_exp_267618-v3_tasks.csv` | `35B53748B71A5F68D9A2F6CF7245A3A30C912E7974419BFA4AEA295781E2D687` |
| `data_exp_272028-v3_task-vcn4.csv` | `0D6EAA27E19D312DF662B7B15E40FD311E3820E008FF6AF0DF328A9507F61E95` |
| `bot_data_exp_268937-v2_task-vcn4.csv` | `AFC4F56D04D3A95FFE8759638C62167980AF389CBFDE9463EB305321A29B1B0B` |
| `data_exp_290516-v1_task-vcn4.csv` | `A4825443A0740CD56E8986F335ACCD8ED0B3DC7A724BE8324494C50C385839D9` |
