# DSA4262 Addictive and Depressive Phone Usage

Final report: [Final Report](Final Report.md)

## Project Summary

This repository contains a behavioural risk modeling project on problematic smartphone use among young adults.

This work was completed by Group 10 for the National University of Singapore (NUS) module DSA4262.

The project uses a dual-engine signal-to-decision framework:

1. Engine 1 (primary): behavioural risk profiling from phone-use patterns.
2. Engine 2 (secondary): PHQ-9 association validation model using phone-use features to estimate risk of PHQ-9 >= 10.

Engine 1 is the primary intervention trigger. Engine 2 is supporting evidence and is not a diagnostic tool.

## Objectives

- Move beyond screen-time-only analysis by modeling behavioural patterns of phone use.
- Produce interpretable, intervention-facing outputs:
	- behavioural risk tier
	- domain score breakdown
	- top behavioural drivers per user
- Validate whether behavioural signals are associated with elevated depressive symptom burden (PHQ-9 threshold validation).

## Data Sources

Primary modeling data:

- data/DSA4262_Survey_Cleaned.csv

Schema/layout reference:

- data/DSA4262_Survey_Cleaned_reorder.csv

Survey wording and source references:

- data/DSA4262_Group_10_Survey_Questions_Survey_Questions_(Final).csv
- data/DSA4262_Group_10_Survey_Questions_Summary.csv
- data/DSA4262 Phone Use Survey.csv

Additional exploratory references:

- pre_exploratory_data/

## Canonical Schema Notes

- Use data/DSA4262_Survey_Cleaned.csv as the canonical input for modeling notebooks.
- Canonical cleaned columns follow Q1_... naming (non-zero-padded).
- data/DSA4262_Survey_Cleaned_reorder.csv uses Q01_... zero-padded names and should be treated as a layout reference.
- Core targets include PHQ9_Total and PHQ9_10plus.

## Modeling Design

### Engine 1 (Primary): Behavioural Risk Engine

Feature scope:

- Phone-use behaviour features only.
- Behavioural blocks mainly from Q4 to Q34 (numeric recoded columns).
- PHQ item responses (Q35 to Q43) are excluded from Engine 1 features.

Theory-driven behavioural domains:

- Exposure and intensity
- Context disruption
- Emotional coping use
- Sleep disruption
- Self-regulation and compulsion

Typical Engine 1 outputs:

- behavioural_risk_tier
- domain_exposure_intensity
- domain_context_disruption
- domain_emotional_coping
- domain_sleep_disruption
- domain_self_regulation
- top_driver_1, top_driver_2, top_driver_3
- optional psu_style_score

### Engine 2 (Secondary): PHQ-9 Validation Model

Target:

- PHQ9_10plus (binary threshold where PHQ9_Total >= 10)

Purpose:

- Validate whether phone-use behavioural signals associate with elevated depressive symptom burden.
- Support future low-friction deployment scenarios where repeated PHQ-9 survey completion may not be feasible.

Representative models compared:

- Logistic Regression (interpretable baseline)
- Random Forest (nonlinear benchmark)
- Gradient Boosting or HistGradientBoosting (optional stress-test model)

Evaluation focus:

- ROC-AUC
- F1
- Recall
- Balanced Accuracy
- Precision
- Confusion matrix and false-positive/false-negative trade-offs

## Key Project Outputs

The integrated signal-to-decision table (often named signal_to_decision_df in notebooks) contains per-user decision support fields, including:

- row_id
- behavioural_risk_tier
- domain score columns
- top behavioural drivers
- optional psu_style_score
- phq9_association_risk_estimate

## Repository Structure

```text
.
|-- Agents.md
|-- Final Report.md
|-- Model_requirement.md
|-- README.md
|-- pyproject.toml
|-- data/
|   |-- DSA4262_Survey_Cleaned.csv
|   |-- DSA4262_Survey_Cleaned_reorder.csv
|   |-- DSA4262 Phone Use Survey.csv
|   |-- DSA4262_Group_10_Survey_Questions_Summary.csv
|   `-- ...
|-- notebooks/
|   |-- behavioural_risk_phq9_validation.ipynb
|   |-- data_processing.ipynb
|   |-- eda.ipynb
|   |-- model.ipynb
|   `-- modelling_9th_April.ipynb
|-- excel_to_csv/
|   `-- excel_to_csv.py
`-- pre_exploratory_data/
```

## Notebook Guide

- notebooks/data_processing.ipynb
	- Cleaning, recoding, and feature preparation.
- notebooks/eda.ipynb
	- Exploratory analysis and behavioural/depression signal exploration.
- notebooks/behavioural_risk_phq9_validation.ipynb
	- Main end-to-end notebook for Engine 1 and Engine 2 integration.
- notebooks/modelling_9th_April.ipynb
	- Latest modeling notebook version.
- notebooks/model.ipynb
	- Earlier or alternative modeling workflow version.

## Setup

Python requirement from pyproject.toml:

- Python >= 3.13

Primary workflow (uv):

```bash
uv sync
```

If you need to add or update a dependency:

```bash
uv add <package-name>
```

Optional fallback (pip):

```bash
pip install -U pip
pip install pandas numpy scikit-learn matplotlib seaborn notebook openpyxl
```

## Running the Analysis

Launch Jupyter in the repository root:

```bash
uv run jupyter notebook
```

Recommended execution order:

1. notebooks/data_processing.ipynb
2. notebooks/eda.ipynb
3. notebooks/modelling_9th_April.ipynb

## Utility Script

excel_to_csv/excel_to_csv.py converts each sheet in an Excel file to separate CSV files.

Example:

```bash
python excel_to_csv/excel_to_csv.py path/to/workbook.xlsx -o path/to/output_dir
```

## Safety and Scope

- This project is intervention-support oriented, not diagnostic.
- Engine 1 behavioural risk drives intervention workflow.
- Engine 2 PHQ association estimate is a secondary contextual signal only.
- False negatives are treated as high-cost in risk validation, while false positives are acceptable for low-intensity follow-up nudges.

## Limitations

- Small sample size and class imbalance reduce generalizability.
- Survey-based self-reporting may introduce recall and response bias.
- Domain weighting and tiering logic require further external validation.

## Team

National University of Singapore, DSA4262 Group 10

- Beckham Toh Yuexi
- Chua Kah Suan
- Kushioka Nodoka
- Nguyen Xuan Nam
- Tian Junjie
- Woo Qi Rui

## Contributions

- Group 10 members led project framing, survey design, analysis decisions, interpretation, and reporting.
- GitHub Copilot contributed coding assistance for data processing workflows, notebook implementation, and model-building iterations.

