# Notebook Implementation Guide: Behavioural Risk Modeling + PHQ-9 Validation

This guide defines exactly how to build a **single notebook** that meets the project brief while keeping model purpose boundaries clear.

---

## 1) Project framing (must appear near top of notebook)

### Main modeling task: behavioural risk model  
**This is the main model.**

- Uses **only phone-use features** (behavioural survey signals; no PHQ-9 items in feature set).
- Produces intervention-facing outputs:
  1. **Domain scores / behavioural dimensions**
  2. **Overall behavioural risk tier**
  3. **Top behavioural drivers**
- Purpose is **behavioural profiling for intervention support**, **not clinical diagnosis**.

### Secondary predictive task: PHQ-9 validation model  
**This is a secondary validation task (not the main intervention trigger).**

- Target: **`PHQ9_10plus`** (PHQ-9 total \(\ge 10\)).
- Purpose: test whether behavioural phone-use signals are associated with elevated depressive symptom burden.
- Deployment rationale: supports future low-friction settings where repeated PHQ-9 surveys may be infeasible.
- Explicit caveat: **do not use this secondary model as the primary intervention trigger.**

---

## 2) Data and variable scope for this repo (schema-grounded)

Use:
- Primary modeling table: `data/DSA4262_Survey_Cleaned.csv`
- Secondary schema reference: `data/DSA4262_Survey_Cleaned_reorder.csv`
- Survey wording/scales reference: 
	- `data/DSA4262_Group_10_Survey_Questions_Survey_Questions_(Final).csv`
	- `data/DSA4262_Group_10_Survey_Questions_Summary.csv`
	- `data/DSA4262 Phone Use Survey.csv` (raw responses)

### Canonical schema notes
- In `DSA4262_Survey_Cleaned.csv`, canonical columns use `Q1_...` format (not zero-padded).
- In `DSA4262_Survey_Cleaned_reorder.csv`, columns are zero-padded (`Q01_...`, `Q02_...`); use this only as layout reference.
- Main modeling should use **`DSA4262_Survey_Cleaned.csv`** to avoid name mismatch across notebooks.

### Required core columns (must exist before modeling)
- Targets/support:
	- `PHQ9_Total`
	- `PHQ9_10plus`
- Behavioural numeric block:
	- `Q4_DailyPhoneTime_num` to `Q34_OthersSayTooMuchUse_num`
- Optional app binary indicators:
	- `Q9_App_SocialMedia`, `Q9_App_Messaging`, `Q9_App_ProductivityStudy`, `Q9_App_WebBrowsing`, `Q9_App_VideoStreaming`, `Q9_App_Gaming`, `Q9_App_Shopping`
- Optional fairness/demographic indicators (not required for main behavioural score):
	- `Q2_Gender_*`, `Q3_Status_*`, `Q1_Age`

### Features for main behavioural model (phone-use only)
Use behavioural items from:
- Exposure/timing: `Q4`–`Q8`, `Q10`
- Context disruption: `Q11`–`Q14`
- Emotional use: `Q15`–`Q17`
- Sleep disruption: `Q18`–`Q21`
- Self-regulation/loss of control: `Q22`–`Q24`
- Optional behavioural severity block: `Q25`–`Q34` (for optional derived PSU-style score)
- Optional app category indicators: `Q9_App_*`

Do **not** include `Q35`–`Q43` PHQ items in main model features.

### Value-range integrity checks (must be explicit in notebook)
- Verify expected numeric ranges:
	- `Q4_DailyPhoneTime_num` in 1–5
	- `Q5_CheckFrequency_num` in 1–4
	- `Q6_AfterWakeCheck_num` in 1–4
	- `Q7_After11PMUse_num` in 1–5
	- `Q8_StopUseAtNight_num` in 1–5
	- `Q10_SocialMediaTime_num` in 1–5
	- `Q11`–`Q24` numeric items in 1–5
	- `Q25`–`Q34` numeric items in 1–6
	- `Q35`–`Q43` numeric PHQ items in 0–3
	- `PHQ9_Total` in 0–27
	- `PHQ9_10plus` binary (`0/1` or `False/True`)
- If boolean columns are read as `True/False`, cast to integer where needed for modeling outputs.

### Ready-to-copy assertion checklist cell (pseudocode only)
Use one dedicated notebook cell early in preprocessing for fail-fast validation.

Pseudocode template:

1) Define required columns
- REQUIRED_COLS = [
	- `PHQ9_Total`, `PHQ9_10plus`,
	- `Q4_DailyPhoneTime_num` ... `Q34_OthersSayTooMuchUse_num`
]

2) Check required columns exist
- missing_cols = columns in REQUIRED_COLS not present in dataframe
- assert missing_cols is empty, else raise error listing missing columns

3) Define range rules
- RANGE_RULES = {
	- `Q4_DailyPhoneTime_num`: (1, 5),
	- `Q5_CheckFrequency_num`: (1, 4),
	- `Q6_AfterWakeCheck_num`: (1, 4),
	- `Q7_After11PMUse_num`: (1, 5),
	- `Q8_StopUseAtNight_num`: (1, 5),
	- `Q10_SocialMediaTime_num`: (1, 5),
	- each of `Q11`–`Q24` numeric: (1, 5),
	- each of `Q25`–`Q34` numeric: (1, 6),
	- each of `Q35`–`Q43` numeric: (0, 3),
	- `PHQ9_Total`: (0, 27)
}

4) Validate ranges
- For each (col, min_val, max_val):
	- out_of_range_mask = non-null values outside [min_val, max_val]
	- assert no out-of-range values, else raise error with column name and offending count

5) Validate `PHQ9_10plus`
- If boolean type, convert to integer 0/1
- assert unique non-null values are subset of {0, 1}

6) Guard main-feature scope
- MAIN_BEHAVIOURAL_FEATURES should include only phone-use behaviour features
- assert no `Q35`–`Q43` or PHQ-derived fields are inside MAIN_BEHAVIOURAL_FEATURES
- assert demographics are excluded from risk-tier construction feature list (unless explicitly in diagnostic-only branch)

7) Optional completeness diagnostics
- Report missingness rate per key feature group (exposure, context, emotional, sleep, self-regulation)
- Warn (not fail) if any key feature missingness exceeds threshold (for example 10%)

8) Pass message
- Print concise summary: schema checks passed, ranges passed, target validation passed

---

## 3) Recommended notebook structure (cell-by-cell blueprint)

## A. Setup and governance
1. **Title + objectives markdown**
   - Include the exact distinction: main behavioural model vs secondary PHQ-9 validation.
2. **Imports + config**
   - `pandas`, `numpy`, `sklearn`, `matplotlib`, `seaborn`.
   - Set random seed and display options.
3. **Data load + quick checks**
   - Row/column shape, missingness, class distribution of `PHQ9_10plus`.

## B. Preprocessing and feature engineering
4. **Ordinal recoding verification**
   - If using precomputed `*_num`, validate ranges and monotonic direction.
   - If recoding in notebook, apply consistent maps from `data_processing.ipynb` logic.
	- Add a fail-fast assertion cell for missing required columns and invalid ranges.
5. **Create behavioural subscale features**
   - Build grouped domain scores as normalized means (e.g., 0–100) for:
	 - Exposure intensity/timing
	 - Context disruption
	 - Emotional coping use
	 - Sleep disruption
	 - Self-regulation/loss of control
   - Keep item-to-domain mapping table in markdown for traceability.
6. **Theory-driven vs data-driven representations**
   - Theory-driven: domain aggregates + optional hand-crafted interactions.
   - Data-driven: standardized item-level matrix (PCA and/or clustering representation).

## C. Main behavioural model (primary intervention model)
7. **Main model input definition**
   - Use phone-use behaviour features only.
	- Exclude demographic and PHQ columns from the main behavioural index by default.
	- Keep demographics only for optional stratified diagnostics (not for risk-tier construction unless explicitly justified).
8. **Construct behavioural risk tiers / profiles**
   - Option A: rule-based quantile tiers from composite behavioural risk index.
   - Option B: cluster profiles (e.g., KMeans) then map clusters to ordered risk tiers via domain severity.
   - Keep mapping explicit and stable.
9. **Driver attribution for the main model**
   - For each user, compute top 2–3 positive contributors from:
	 - weighted domain gap-to-baseline, or
	 - interpretable model coefficients / permutation importance.
10. **Main model outputs table (`signal_to_decision_df`)**
	- One row per user with:
	  - `behavioural_risk_tier`
	  - domain score columns
	  - `top_driver_1..3`
	  - optional `psu_style_score`

## D. Secondary PHQ-9 validation model (separate section)
11. **Secondary task declaration markdown**
	- State again: not the main intervention trigger.
12. **Train interpretable predictive models for `PHQ9_10plus`**
	- Candidate models:
	  - Logistic Regression (`class_weight='balanced'`)
	  - Random Forest (for nonlinear benchmark)
	  - Gradient Boosting / HistGradientBoosting (optional third benchmark)
13. **Cross-validated evaluation**
	- Stratified K-fold CV.
	- Capture fold-wise and mean metrics.
	- Keep folds reproducible (`random_state` fixed).
14. **Threshold analysis**
	- Evaluate multiple thresholds (e.g., 0.30 / 0.40 / 0.50).
	- Show precision-recall trade-offs.
15. **Secondary output column**
	- Add `phq9_association_risk_estimate` (probability from selected validation model) into final output table.

## E. Model comparison, error analysis, and interpretation
16. **Model comparison panel**
	- List compared models + rationale:
	  - Logistic Regression: transparent, stable baseline
	  - Random Forest: nonlinear interactions
	  - Boosting model: performance stress test
17. **Metrics required by brief**
	- ROC-AUC
	- F1
	- Recall
	- Balanced Accuracy
18. **Class balance considerations**
	- Report prevalence of `PHQ9_10plus`.
	- Use stratified CV + class weighting.
19. **Error analysis**
	- Confusion matrix at chosen threshold.
	- Characterize false positives vs false negatives.
	- Explain intervention consequences:
	  - FN cost: missed at-risk users
	  - FP cost: unnecessary low-intensity nudges
20. **Interpretability statement**
	- Explain why interpretable modeling is prioritized for intervention trust and actionable messaging.

## F. Final “Signal to Decision” section (required)
21. Produce and display final output schema per user:
	- `behavioural_risk_tier`
	- domain breakdown columns
	- top 2–3 behavioural drivers
	- optional `psu_style_score`
	- secondary `phq9_association_risk_estimate`
	- Include stable user key for row traceability (`row_id` or index-based ID).
22. Add one markdown block clarifying operational policy:
	- Main behavioural risk tier drives intervention workflow.
	- PHQ-9 association estimate is validation/supporting evidence only.

## G. Example users walkthrough (required final section)
23. Add a section titled **Example users** after Engine 1 and Engine 2 outputs are complete.
24. Select exactly **3 contrasting users** from the final table (for example: one low-tier, one moderate-tier, one high-tier, or any three profiles that meaningfully differ).
25. For each selected user, show a compact per-user trace with at least:
	- `row_id`
	- Engine 1 output: `behavioural_risk_tier`
	- Engine 1 domain profile: all domain score columns
	- Engine 1 attribution: `top_driver_1`, `top_driver_2`, `top_driver_3`
	- Engine 2 output: `phq9_association_risk_estimate`
26. Add a short interpretation paragraph per user that explains:
	- why Engine 1 placed the user in that behavioural tier,
	- how Engine 2 probability compares with Engine 1 risk tier,
	- whether signals are aligned (high-high / low-low) or mixed (for example high tier but moderate PHQ association).
27. Add a final comparative summary across the 3 users that explicitly demonstrates:
	- Engine 1 provides the primary intervention trigger and behavioural explanation,
	- Engine 2 adds supporting mental-health association context,
	- both engines together provide richer decision support than either engine alone.

### Recommended implementation pattern for the notebook cell
Use one code cell to:
- create a sorted view of the final `signal_to_decision_df`,
- pick 3 representative `row_id` values,
- display those rows side-by-side,
- print a concise text interpretation scaffold for each selected user.

Use one markdown cell immediately after to write the human-readable interpretation and cross-user comparison.

---

## 4) Concrete domain mapping template for this dataset

Use this as default mapping unless revised with documented reason:

- **Exposure / intensity**: `Q4_DailyPhoneTime_num`, `Q5_CheckFrequency_num`, `Q6_AfterWakeCheck_num`, `Q7_After11PMUse_num`, `Q8_StopUseAtNight_num`, `Q10_SocialMediaTime_num`
- **Context disruption**: `Q11_PhoneDuringMeals_num`, `Q12_PhoneDuringWorkClass_num`, `Q13_CheckDuringTasks_num`, `Q14_NotificationsInterrupt_num`
- **Emotional coping use**: `Q15_UseWhenBored_num`, `Q16_UseWhenStressed_num`, `Q17_DistractNegativeEmotions_num`
- **Sleep disruption**: `Q18_PhoneInBed_num`, `Q19_PhoneDelaysSleep_num`, `Q20_NotificationsWakeNight_num`, `Q21_WakeToCheckPhone_num`
- **Self-regulation / compulsion**: `Q22_UnlockWithoutReason_num`, `Q23_UseLongerThanIntended_A_num`, `Q24_FailToReduceUse_num`
- **Optional PSU-style severity score block**: `Q25_MissPlannedWork_num` to `Q34_OthersSayTooMuchUse_num`

---

## 5) Minimal acceptance checklist (for notebook completion)

The notebook is complete only if all are true:

- Clear top-level separation between **main behavioural model** and **secondary PHQ-9 validation**.
- Main model explicitly states it uses phone-use features only.
- Main model outputs domain scores, overall tier, and top drivers.
- Secondary model explicitly targets `PHQ9_10plus` and is marked non-primary trigger.
- Pipeline includes recoding, subscales, theory vs data-driven representations, risk tiers, interpretable PHQ model, and interpretation.
- Model comparison includes why each model was chosen.
- Evaluation includes CV, class balance strategy, threshold thinking, and required metrics (ROC-AUC, F1, recall, balanced accuracy).
- Final notebook includes an **Example users** section with 3 contrasting users showing Engine 1 outputs + Engine 2 estimate and a comparative interpretation of how both engines work together.
- Error analysis discusses FP vs FN trade-offs.
- Final signal-to-decision table includes all required user-level outputs.
- Notebook includes schema validation checks tied to actual CSV column names and expected ranges.

---

## 6) Scope guardrails

- Keep this notebook intervention-facing and interpretable.
- Avoid diagnosis language; use behavioural risk language.
- Do not merge main and secondary tasks into one objective.
- Do not use PHQ item responses as predictors in the main behavioural model.

