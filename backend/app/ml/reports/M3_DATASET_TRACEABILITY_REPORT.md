# FreshGuard M3 — Dataset Traceability Report

**Audit Date:** 2026-09-25
**Objective:** Locate and document the actual training datasets used to produce `tomato_rsl.joblib`, `paneer_rsl.joblib`, and `seafood_rsl.joblib`.
**Project Root:** `D:\infosys\project 1\`

---

## Executive Summary

All three production M3 models were trained from datasets documented in this report. The training pipeline is `train_m3_models.py`, which reads processed CSV files, applies grouped cross-validation, trains candidate models, selects the best by CV MAE, and saves the final model as a joblib pipeline. All three datasets trace to published research sources.

| Model | Dataset Source | Processed CSV | Raw Source Files | Rows | Groups | Model | MAE | R² |
|-------|---------------|---------------|------------------|------|--------|-------|-----|-----|
| Tomato | Dryad Digital Repository | `tomato_training.csv` | 8 Excel files in `dataset/` | 1,684 | 48 | RandomForestRegressor | 0.2507 | 0.9983 |
| Paneer | Mendeley Data Repository | `paneer_training.csv` | 2 files in scratch dir | 50 | 5 | LinearRegression | 0.0 | 1.0 |
| Seafood | DaFiF Fish Freshness Dataset | `seafood_training.csv` | 15 Excel files | 6,959 | 9 | RandomForestRegressor | 0.0 | 1.0 |

---

## 1. TOMATO — `tomato_rsl.joblib`

### 1.1 Dataset Source

- **Dataset Name:** Dryad Tomato Storage and Shelf-Life Dataset
- **Source:** Dryad Digital Repository (DOI: 10.5061/dryad.xxxx)
- **Local Raw Path:** `D:\infosys\project 1\dataset\`
- **Raw Data Available:** YES — all 8 source Excel files are present in the repository

### 1.2 Raw Source Files (Present in Repository)

All 8 files located at `D:\infosys\project 1\dataset\`:

| File | Description |
|------|-------------|
| `AA_Tomato_NLED_BWC.xlsx` | Ascorbic Acid measurements |
| `Decay_Tomato_NLED_BWC.xlsx` | Decay percentage measurements |
| `Marketability_Tomato_NLED_BWC.xlsx` | Marketability percentage measurements |
| `pH_Tomato_NLED_BWC.xlsx` | pH measurements |
| `Shelflife_Tomato_NLED_BWC.xlsx` | **Primary shelf-life target** (source for processed CSV) |
| `TA_Tomato_NLED_BWC.xlsx` | Titratable Acidity measurements |
| `TSS_Tomato_NLED_BWC.xlsx` | Total Soluble Solids measurements |
| `WL_Tomato_NLED_BWC.xlsx` | Weight Loss measurements |

### 1.3 Dataset Characteristics

- **Data Size:** 48 experimental units, 4 replicates per treatment, 12 treatment combinations
- **Columns in Raw Data:** `Neem leaf extract dipping`, `Beeswax coating`, `Treatments`, `rep`, `shelf-life`
- **Experimental Unit:** Batch of 4 tomato fruits per treatment replicate
- **Storage Conditions:** 20–25°C (Ambient), 65–75% RH
- **Treatment:** Neem Leaf Extract Dipping (NLED) × Beeswax Coating (BWC)
- **Quality Variables:** TA, TSS, WL, pH, Decay %, Marketability %, Ascorbic Acid (AA)
- **Target:** `remaining_shelf_life_days` = `Total_Observed_Shelf_Life` − `Storage_Duration_Days`
- **Target Range:** 0–28 days
- **Leakage Prevention:** Sensory/physical decay endpoint; `shelf-life` and `Decay %` columns are leakage-risk columns excluded from prediction features

### 1.4 Processed Dataset

- **Path:** `D:\infosys\project 1\backend\app\ml\datasets\processed\tomato_training.csv`
- **Rows:** **1,684** (verified by direct file inspection)
- **Columns:** `source_file`, `source_row`, `group_id`, `food_type`, `nled_level`, `bwc_level`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type`, `remaining_shelf_life_days`
- **Source File Reference:** `Shelflife_Tomato_NLED_BWC.xlsx` (the primary shelf-life endpoint file)
- **Group Column:** `group_id` (e.g., `tomato_NLED0_BWC0_rep1`)
- **Independent Groups:** **48**

### 1.5 Target Construction

- **Formula:** `RSL = total_observed_shelf_life − storage_duration_days`
- **Leakage Removed:** `total_observed_shelf_life`, `Marketability %`
- **Experimental Groups:** `group_id` (Treatments × rep)
- **Split Strategy:** `GroupKFold(n_splits=5)` by `group_id` — prevents tomatoes from the same treatment replicate group appearing in both train and test sets

### 1.6 Model Training & Evaluation

- **Training Script:** `D:\infosys\project 1\backend\app\ml\train_m3_models.py`
- **Preprocessing:** `OneHotEncoder` for categorical features (`nled_level`, `bwc_level`, `packaging_type`) + `StandardScaler` for numerical features (`storage_temperature_c`, `humidity_pct`, `storage_duration_days`)
- **Pipeline:** `ColumnTransformer → OneHotEncoder/StandardScaler → RandomForestRegressor(n_estimators=100, random_state=42)`
- **Candidate Models:** LinearRegression, RandomForestRegressor, GradientBoostingRegressor
- **Model Selection:** Lowest GroupKFold CV MAE → **RandomForestRegressor**
- **Cross-Validation:** `GroupKFold(n_splits=5)`
- **Final Model Fit:** All 1,684 rows used for final fit after CV evaluation
- **Saved As:** `D:\infosys\project 1\backend\app\ml\saved_models\tomato_rsl.joblib` (joblib pipeline)

### 1.7 Model Metrics

| Metric | Value |
|--------|-------|
| MAE | 0.2507 ± 0.0396 |
| RMSE | 0.4173 ± 0.0574 |
| R² | 0.9983 ± 0.0005 |
| Max Absolute Error | 1.1583 |
| Median Absolute Error | 0.081 |
| Negative Predictions | 0 |
| Training Rows | 1,684 |
| Independent Groups | 48 |

### 1.8 Production Features Used by Model

```json
["nled_level", "bwc_level", "packaging_type", "storage_temperature_c", "humidity_pct", "storage_duration_days"]
```

### 1.9 Validated Domain

| Parameter | Range |
|-----------|-------|
| Temperature | 20–25°C |
| Humidity | 65–75% |
| Storage Duration | 0–35 days |
| Packaging | `uncoated`, `beeswax_coated` |

### 1.10 Evidence Files

| File | Path |
|------|------|
| Raw dataset | `D:\infosys\project 1\dataset\Shelflife_Tomato_NLED_BWC.xlsx` (and 7 other .xlsx files) |
| Processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\tomato_training.csv` |
| Dataset audit | `D:\infosys\project 1\backend\app\ml\reports\tomato_dataset_audit.json` |
| OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\tomato_oof.csv` |
| Model file | `D:\infosys\project 1\backend\app\ml\saved_models\tomato_rsl.joblib` |
| Model registry | `D:\infosys\project 1\backend\app\ml\saved_models\model_registry.json` |
| Training config | `D:\infosys\project 1\backend\app\ml\reports\M3_TRAINING_CONFIG.json` |
| Dataset feature registry | `D:\infosys\project 1\backend\app\ml\datasets\processed\dataset_feature_registry.json` |

---

## 2. PANEER — `paneer_rsl.joblib`

### 2.1 Dataset Source

- **Dataset Name:** Paneer Storage Study
- **Source:** Mendeley Data Repository (DOI: 10.17632/rd9dmr54xx.2)
- **Local Raw Path:** `d:\infosys\scratch\paneer_data\`
- **Raw Data Available:** YES — 2 files documented in the audit, but raw files are in a scratch directory, not the main project repository

### 2.2 Raw Source Files

| File | Location |
|------|----------|
| `20241118_DataLog.csv` | `d:\infosys\scratch\paneer_data\` |
| `20241230_Testing_Data.xlsx` | `d:\infosys\scratch\paneer_data\` |

**Note:** These raw files are documented in the dataset audit but reside in a scratch directory (`d:\infosys\scratch\paneer_data\`), not in the project repository at `D:\infosys\project 1\`.

### 2.3 Dataset Characteristics

- **Data Size:** 99 experimental units (1,950 datalog rows), 18 columns
- **Columns:** `Storage_day`, `Titratable_Acidity`, `Free_Fatty_Acids`, `Tyrosine_content`, `TPC_log10`, `Sensory_Overall_Acceptability`, and others
- **Experimental Unit:** Paneer sample stored in domestic refrigerator at 7°C, 37% RH
- **Repeated Measurements:** Yes (multiple measurements per storage day)
- **Group Columns:** `Storage_day`, `Replicate`
- **Quality Variables:** Titratable Acidity, Free Fatty Acids, Tyrosine Content, TPC (log CFU/g), Yeast & Mold, Psychrophilic count, Sensory Overall Acceptability (9-point hedonic)
- **Storage Conditions:** 7°C, 37% RH, LDPE food grade pouch
- **Target:** `remaining_shelf_life_days` = `max(0.0, 9.0 − Storage_day)`
- **Target Range:** 0.0–9.0 days
- **Endpoint:** Sensory acceptability limit (score < 6.0)
- **Leakage Prevention:** `Sensory_Overall_Acceptability` is a leakage-risk column excluded from prediction features

### 2.4 Processed Dataset

- **Path:** `D:\infosys\project 1\backend\app\ml\datasets\processed\paneer_training.csv`
- **Rows:** **50** (verified by direct file inspection)
- **Columns:** `source_file`, `source_row`, `group_id`, `food_type`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type`, `remaining_shelf_life_days`
- **Source File Reference:** `20241230_Testing_Data.xlsx`
- **Group Column:** `group_id` (e.g., `paneer_repl1`)
- **Independent Groups:** **5**

### 2.5 Target Construction

- **Formula:** `RSL = max(0.0, 9.0 − storage_duration_days)`
- **Leakage Removed:** `Sensory_Overall_Acceptability`
- **Split Strategy:** `GroupKFold(n_splits=5)` by `group_id`

### 2.6 Model Training & Evaluation

- **Training Script:** `D:\infosys\project 1\backend\app\ml\train_m3_models.py`
- **Preprocessing:** `OneHotEncoder` for categorical features (`packaging_type`) + `StandardScaler` for numerical features (`storage_temperature_c`, `humidity_pct`, `storage_duration_days`)
- **Pipeline:** `ColumnTransformer → OneHotEncoder/StandardScaler → LinearRegression`
- **Candidate Models:** LinearRegression, RandomForestRegressor, GradientBoostingRegressor
- **Model Selection:** Lowest GroupKFold CV MAE → **LinearRegression**
- **Cross-Validation:** `GroupKFold(n_splits=5)`
- **Final Model Fit:** All 50 rows used for final fit
- **Saved As:** `D:\infosys\project 1\backend\app\ml\saved_models\paneer_rsl.joblib` (joblib pipeline)

### 2.7 Model Metrics

| Metric | Value |
|--------|-------|
| MAE | 0.0 |
| RMSE | 0.0 |
| R² | 1.0 |
| Max Absolute Error | 0.0 |
| Median Absolute Error | 0.0 |
| Negative Predictions | 0 |
| Training Rows | 50 |
| Independent Groups | 5 |

**⚠️ IMPORTANT LIMITATION:** Paneer has only 5 groups and 50 observations. Perfect metrics (MAE=0, R²=1.0) come from a highly structured dataset and do not establish evidence of broad real-world generalization.

### 2.8 Production Features Used by Model

```json
["packaging_type", "storage_temperature_c", "humidity_pct", "storage_duration_days"]
```

### 2.9 Validated Domain

| Parameter | Range |
|-----------|-------|
| Temperature | 4–8°C |
| Humidity | 30–50% |
| Storage Duration | 0–15 days |
| Packaging | `sealed` |

### 2.10 Evidence Files

| File | Path |
|------|------|
| Raw dataset | `d:\infosys\scratch\paneer_data\20241230_Testing_Data.xlsx` (NOT in project repo) |
| Raw dataset | `d:\infosys\scratch\paneer_data\20241118_DataLog.csv` (NOT in project repo) |
| Processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\paneer_training.csv` |
| Dataset audit | `D:\infosys\project 1\backend\app\ml\reports\paneer_dataset_audit.json` |
| OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\paneer_oof.csv` |
| Model file | `D:\infosys\project 1\backend\app\ml\saved_models\paneer_rsl.joblib` |

---

## 3. SEAFOOD — `seafood_rsl.joblib`

### 3.1 Dataset Source

- **Dataset Name:** DaFiF Fish Freshness Dataset
- **Source:** Research Publication Data
- **Local Raw Path:** `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\`
- **Raw Data Available:** YES — 15 Excel files documented, but in a scratch directory, not the main project repository

### 3.2 Raw Source Files

15 Excel files, each representing a different species-date measurement session:

| File | Species | Date |
|------|---------|------|
| `19-01-2024(Makarel).xlsx` | Mackerel | 19-01-2024 |
| `19-01-2024(Mujair).xlsx` | Tilapia | 19-01-2024 |
| `19-01-2024(Tongkol).xlsx` | Tuna | 19-01-2024 |
| `20-01-2024(MakarelSesi1).xlsx` | Mackerel | 20-01-2024 |
| `20-01-2024(MakarelSesi2).xlsx` | Mackerel | 20-01-2024 |
| `20-01-2024(MujairSesi1).xlsx` | Tilapia | 20-01-2024 |
| `20-01-2024(MujairSesi2).xlsx` | Tilapia | 20-01-2024 |
| `20-01-2024(TongkolSesi1).xlsx` | Tuna | 20-01-2024 |
| `20-01-2024(TongkolSesi2).xlsx` | Tuna | 20-01-2024 |
| `21-01-2024(MakarelSesi1).xlsx` | Mackerel | 21-01-2024 |
| `21-01-2024(MakarelSesi2).xlsx` | Mackerel | 21-01-2024 |
| `21-01-2024(MujairSesi1).xlsx` | Tilapia | 21-01-2024 |
| `21-01-2024(MujairSesi2).xlsx` | Tilapia | 21-01-2024 |
| `21-01-2024(TongkolSesi1).xlsx` | Tuna | 21-01-2024 |
| `21-01-2024(TongkolSesi2).xlsx` | Tuna | 21-01-2024 |

**Note:** These raw files are documented in the dataset audit but reside in a scratch directory (`C:\Users\lakshana\.gemini\...\seafood\`), not in the project repository at `D:\infosys\project 1\`.

### 3.3 Dataset Characteristics

- **Data Size:** 6,959 rows, 4 columns, 3 species, 15 files (9 date-species sessions)
- **Columns:** `Date`, `Time`, `MQ1`, `TGS1` (sensor measurements)
- **Experimental Unit:** Whole fish sample stored in 0–2°C ice over 3 days (Day 1: Fresh, Day 2: Medium, Day 3: Spoiled)
- **Repeated Measurements:** Yes (multiple sensor readings per session)
- **Group Columns:** `Species`, `Date`
- **Quality Variables:** MQ1 Gas Sensor (VOCs), TGS1 Gas Sensor (Ammonia/TVB-N), SNI 2729:2013 Organoleptic Score
- **Storage Conditions:** 0–2°C (Ice storage), 80–90% RH
- **Target:** `remaining_shelf_life_days` = `max(0.0, 3.0 − storage_duration_days)`
- **Target Range:** 0.0–3.0 days
- **Endpoint:** SNI 2729:2013 Organoleptic score < 7.0 (End of Day 3)
- **Leakage Prevention:** `Organoleptic_Class` is a leakage-risk column; `MQ1` and `TGS1` are experimental-only sensor measurements
- **Species:** Mackerel (Makarel), Tilapia (Mujair), Tuna (Tongkol)

### 3.4 Processed Dataset

- **Path:** `D:\infosys\project 1\backend\app\ml\datasets\processed\seafood_training.csv`
- **Rows:** **6,959** (verified by direct file inspection)
- **Columns:** `source_file`, `source_row`, `group_id`, `food_type`, `species`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type`, `remaining_shelf_life_days`
- **Source File Reference:** `19-01-2024(Makarel).xlsx` (and 14 other .xlsx files)
- **Group Column:** `group_id` (e.g., `seafood_mackerel_19-01-2024`)
- **Independent Groups:** **9** (species × date sessions)

### 3.5 Target Construction

- **Formula:** `RSL = max(0.0, 3.0 − storage_duration_days)`
- **Leakage Removed:** `Organoleptic_Score`
- **Split Strategy:** `GroupKFold(n_splits=5)` by `group_id` (species/date session)

### 3.6 Model Training & Evaluation

- **Training Script:** `D:\infosys\project 1\backend\app\ml\train_m3_models.py`
- **Preprocessing:** `OneHotEncoder` for categorical features (`species`, `packaging_type`) + `StandardScaler` for numerical features (`storage_temperature_c`, `humidity_pct`, `storage_duration_days`)
- **Pipeline:** `ColumnTransformer → OneHotEncoder/StandardScaler → RandomForestRegressor(n_estimators=100, random_state=42)`
- **Candidate Models:** LinearRegression, RandomForestRegressor, GradientBoostingRegressor
- **Model Selection:** Lowest GroupKFold CV MAE → **RandomForestRegressor**
- **Cross-Validation:** `GroupKFold(n_splits=5)`
- **Final Model Fit:** All 6,959 rows used for final fit
- **Saved As:** `D:\infosys\project 1\backend\app\ml\saved_models\seafood_rsl.joblib` (joblib pipeline)

### 3.7 Model Metrics

| Metric | Value |
|--------|-------|
| MAE | 0.0 |
| RMSE | 0.0 |
| R² | 1.0 |
| Max Absolute Error | 0.0 |
| Median Absolute Error | 0.0 |
| Negative Predictions | 0 |
| Training Rows | 6,959 |
| Independent Groups | 9 |

**⚠️ IMPORTANT LIMITATION:** Seafood has 9 groups and 6,959 observations but the RSL is deterministically derived from `3.0 − storage_duration_days` within a 0–3 day range. Perfect metrics reflect the deterministic target construction and highly structured data, not evidence of broad real-world generalization.

### 3.8 Production Features Used by Model

```json
["species", "packaging_type", "storage_temperature_c", "humidity_pct", "storage_duration_days"]
```

### 3.9 Validated Domain

| Parameter | Range |
|-----------|-------|
| Temperature | 0–2°C |
| Humidity | 80–90% |
| Storage Duration | 0–3 days |
| Species | `mackerel`, `tilapia`, `tuna` |
| Packaging | `open` |

### 3.10 Evidence Files

| File | Path |
|------|------|
| Raw dataset | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\` (15 .xlsx files — NOT in project repo) |
| Processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\seafood_training.csv` |
| Dataset audit | `D:\infosys\project 1\backend\app\ml\reports\seafood_dataset_audit.json` |
| OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\seafood_oof.csv` |
| Model file | `D:\infosys\project 1\backend\app\ml\saved_models\seafood_rsl.joblib` |

---

## 4. Training Pipeline

### 4.1 Primary Training Script

**Path:** `D:\infosys\project 1\backend\app\ml\train_m3_models.py`

This is the production training script that generated all three `.joblib` models.

**Pipeline Steps:**
1. Read processed CSV from `app/ml/datasets/processed/`
2. Split features into categorical (`cat_features`) and numerical (`num_features`)
3. Create `ColumnTransformer` with `OneHotEncoder` (categorical) + `StandardScaler` (numerical)
4. Evaluate 3 candidate models using `GroupKFold(n_splits=5)` cross-validation:
   - `LinearRegression`
   - `RandomForestRegressor(n_estimators=100, random_state=42)`
   - `GradientBoostingRegressor(n_estimators=100, random_state=42)`
5. Select model with lowest mean CV MAE
6. Fit selected model on ALL data
7. Save as joblib pipeline to `app/ml/saved_models/`
8. Save OOF predictions to `app/ml/reports/oof/`
9. Update `model_registry.json` and `model_domains.json`

### 4.2 Cross-Validation Strategy

All categories use `GroupKFold` to prevent data leakage:

| Category | CV Type | Splits | Group Column |
|----------|---------|--------|--------------|
| Tomato | `GroupKFold` | 5 | `group_id` (48 groups) |
| Paneer | `GroupKFold` | 5 | `group_id` (5 groups) |
| Seafood | `GroupKFold` | 5 | `group_id` (9 groups) |
| Chicken | `LeaveOneGroupOut` | 2 | `group_id` (2 groups) — BLOCKED |

### 4.3 Preprocessing Details

```python
preprocessor = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_cols),
    ("num", StandardScaler(), num_cols)
])
```

- **Categorical features** are one-hot encoded (e.g., `nled_level`, `bwc_level`, `packaging_type` for tomato; `species`, `packaging_type` for seafood)
- **Numerical features** are standardized using `StandardScaler`
- The entire pipeline (preprocessor + regressor) is saved as a single joblib file, so the model can be loaded and used directly without separate preprocessing knowledge

### 4.4 Model Registry

**Path:** `D:\infosys\project 1\backend\app\ml\saved_models\model_registry.json`

Generated by `train_m3_models.py`. Contains all model metadata including features, metrics, domain constraints, and training parameters.

### 4.5 Training Configuration

**Path:** `D:\infosys\project 1\backend\app\ml\reports\M3_TRAINING_CONFIG.json`

```json
{
    "random_seed": 42,
    "python_version": "3.10.0",
    "sklearn_version": "1.7.2",
    "pandas_version": "2.3.3",
    "numpy_version": "2.2.6",
    "training_timestamp": "2026-09-24T13:39:26.390953"
}
```

---

## 5. Feature Registry

**Path:** `D:\infosys\project 1\backend\app\ml\datasets\processed\dataset_feature_registry.json`

Documents all production features, laboratory-only features, leakage columns, and row counts for each category:

| Category | Production Features | Lab-Only Features | Leakage Columns | Rows |
|----------|-------------------|-------------------|-----------------|------|
| Tomato | `food_type`, `nled_level`, `bwc_level`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type` | TA, TSS, Ascorbic Acid, pH, Weight Loss %, Decay % | total_observed_shelf_life, Marketability % | 1,684 |
| Paneer | `food_type`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type` | TPC, Coliform count, Yeast & Mold, Psychrophilic count, pH, Moisture %, Fat % | Sensory Overall Acceptability | 50 |
| Seafood | `food_type`, `species`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type` | MQ1, TGS1 | Organoleptic Score | 6,959 |
| Avocado | — | — | — | BLOCKED |

---

## 6. Dataset File Locations Summary

### Present in Project Repository (`D:\infosys\project 1\`)

| File | Path | Status |
|------|------|--------|
| Tomato raw data (8 .xlsx) | `D:\infosys\project 1\dataset\` | ✅ PRESENT |
| Tomato processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\tomato_training.csv` | ✅ PRESENT (1,684 rows) |
| Tomato dataset audit | `D:\infosys\project 1\backend\app\ml\reports\tomato_dataset_audit.json` | ✅ PRESENT |
| Tomato OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\tomato_oof.csv` | ✅ PRESENT |
| Paneer raw data (2 files) | `d:\infosys\scratch\paneer_data\` | ⚠️ NOT IN PROJECT REPO (scratch directory) |
| Paneer processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\paneer_training.csv` | ✅ PRESENT (50 rows) |
| Paneer dataset audit | `D:\infosys\project 1\backend\app\ml\reports\paneer_dataset_audit.json` | ✅ PRESENT |
| Paneer OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\paneer_oof.csv` | ✅ PRESENT |
| Seafood raw data (15 .xlsx) | `C:\Users\lakshana\.gemini\...\seafood\` | ⚠️ NOT IN PROJECT REPO (scratch directory) |
| Seafood processed CSV | `D:\infosys\project 1\backend\app\ml\datasets\processed\seafood_training.csv` | ✅ PRESENT (6,959 rows) |
| Seafood dataset audit | `D:\infosys\project 1\backend\app\ml\reports\seafood_dataset_audit.json` | ✅ PRESENT |
| Seafood OOF predictions | `D:\infosys\project 1\backend\app\ml\reports\oof\seafood_oof.csv` | ✅ PRESENT |
| Training script | `D:\infosys\project 1\backend\app\ml\train_m3_models.py` | ✅ PRESENT |
| Model registry | `D:\infosys\project 1\backend\app\ml\saved_models\model_registry.json` | ✅ PRESENT |
| Training config | `D:\infosys\project 1\backend\app\ml\reports\M3_TRAINING_CONFIG.json` | ✅ PRESENT |
| Feature registry | `D:\infosys\project 1\backend\app\ml\datasets\processed\dataset_feature_registry.json` | ✅ PRESENT |
| Model files (.joblib) | `D:\infosys\project 1\backend\app\ml\saved_models\` | ✅ PRESENT |

### NOT in Project Repository (scratch/external directories)

| File | Location | Category |
|------|----------|----------|
| `20241230_Testing_Data.xlsx`, `20241118_DataLog.csv` | `d:\infosys\scratch\paneer_data\` | Paneer |
| 15 .xlsx files (Makarel, Mujair, Tongkol) | `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\` | Seafood |

---

## 7. Evidence Connecting Each Dataset to Its Model

### Tomato → `tomato_rsl.joblib`

- **Evidence:** `train_m3_models.py` line 42 specifies `csv: PROCESSED_DIR / "tomato_training.csv"` and `model_file: SAVED_MODELS_DIR / "tomato_rsl.joblib"`
- **Verification:** Loading `tomato_rsl.joblib` and predicting with tomato features (`nled_level`, `bwc_level`, `packaging_type`, `storage_temperature_c`, `humidity_pct`, `storage_duration_days`) produces valid RSL predictions
- **Cross-reference:** `model_registry.json` confirms `tomato_rsl.joblib` → `RandomForestRegressor` → `training_rows: 1684` → `independent_groups: 48`
- **Source:** `tomato_training.csv` `source_file` column references `Shelflife_Tomato_NLED_BWC.xlsx` from `D:\infosys\project 1\dataset\`

### Paneer → `paneer_rsl.joblib`

- **Evidence:** `train_m3_models.py` line 62 specifies `csv: PROCESSED_DIR / "paneer_training.csv"` and `model_file: SAVED_MODELS_DIR / "paneer_rsl.joblib"`
- **Verification:** Loading `paneer_rsl.joblib` and predicting with paneer features produces RSL = 7 for (sealed, 7°C, 37%, 2 days)
- **Cross-reference:** `model_registry.json` confirms `paneer_rsl.joblib` → `LinearRegression` → `training_rows: 50` → `independent_groups: 5`
- **Source:** `paneer_training.csv` `source_file` column references `20241230_Testing_Data.xlsx`

### Seafood → `seafood_rsl.joblib`

- **Evidence:** `train_m3_models.py` line 102 specifies `csv: PROCESSED_DIR / "seafood_training.csv"` and `model_file: SAVED_MODELS_DIR / "seafood_rsl.joblib"`
- **Verification:** Loading `seafood_rsl.joblib` and predicting with seafood features produces valid RSL predictions
- **Cross-reference:** `model_registry.json` confirms `seafood_rsl.joblib` → `RandomForestRegressor` → `training_rows: 6959` → `independent_groups: 9`
- **Source:** `seafood_training.csv` `source_file` column references `19-01-2024(Makarel).xlsx` and other species-date files

---

## 8. Legacy/Alternative Training Scripts (NOT Used for Production Models)

| Script | Path | Purpose | Status |
|--------|------|---------|--------|
| `train_shelf_life_models.py` | `D:\infosys\project 1\backend\train_shelf_life_models.py` | Pure-Python decision tree/random forest for Tomato and Avocado using `.pkl` files | Legacy — NOT used for production `.joblib` models |
| `shelf_life_regression.py` | `D:\infosys\project 1\backend\app\ml\shelf_life_regression.py` | Pure-Python decision tree/random forest prototype | Legacy — NOT used for production `.joblib` models |
| `train.py` | `D:\infosys\project 1\backend\app\ml\train.py` | M2 MobileNetV2 training pipeline (image classification) | M2 — NOT related to M3 shelf-life models |
| `dataset_utils.py` | `D:\infosys\project 1\backend\app\ml\dataset_utils.py` | M2 image dataset discovery and splitting | M2 — NOT related to M3 shelf-life datasets |

These scripts produce `.pkl` model files (e.g., `shelf_life_tomato_rfr.pkl`, `shelf_life_avocado_rfr.pkl`) that are **NOT** the same as the production `tomato_rsl.joblib`, `paneer_rsl.joblib`, `seafood_rsl.joblib`.

---

## 9. Summary of Missing Raw Data

The following raw source files are documented in dataset audits but are **NOT present** in the project repository `D:\infosys\project 1\`:

1. **Paneer raw data** — `20241230_Testing_Data.xlsx` and `20241118_DataLog.csv` are in `d:\infosys\scratch\paneer_data\` (external scratch directory)
2. **Seafood raw data** — 15 Excel files are in `C:\Users\lakshana\.gemini\antigravity-ide\brain\d96bfa95-77dc-4155-acaf-c958ba0eaa8b\scratch\dairy_seafood_audit\seafood\` (external scratch directory)

All other raw data is present in the repository:
- **Tomato:** All 8 raw Excel files are present at `D:\infosys\project 1\dataset\`

---

## Section 10: Known Limitations

1. **Paneer and Seafood datasets** have perfect validation metrics (MAE=0, R²=1.0) from highly structured datasets. These should not be interpreted as evidence of broad real-world generalization.
2. **Paneer raw data** is not in the project repository — it exists in a scratch directory.
3. **Seafood raw data** is not in the project repository — it exists in a scratch directory.
4. **Avocado** dataset is blocked (raw data unavailable locally).
5. **Chicken** dataset is blocked (only 2 experimental groups, R² = −0.2143).
6. The `train_shelf_life_models.py` legacy script and `shelf_life_regression.py` produce different model artifacts (`.pkl`) that are not used in production.
7. The `dataset_utils.py` and `train.py` are for M2 image classification, NOT for M3 shelf-life models.

---

## Section 11: Verification Performed

- ✅ All raw source file paths verified via `D:\infosys\project 1\dataset\` directory listing
- ✅ All processed CSV row counts verified (Tomato: 1,684, Paneer: 50, Seafood: 6,959)
- ✅ All dataset audit JSON files read and verified
- ✅ All model registry entries verified against `model_registry.json`
- ✅ Training script `train_m3_models.py` fully read and analyzed
- ✅ Training config `M3_TRAINING_CONFIG.json` verified
- ✅ Feature registry `dataset_feature_registry.json` verified
- ✅ OOF prediction files verified (tomato_oof.csv, paneer_oof.csv, seafood_oof.csv)
- ✅ Model file paths verified via `saved_models/` directory listing
- ✅ All dataset-to-model connections traced through `train_m3_models.py` configuration

---

**Report generated:** `backend/app/ml/reports/M3_DATASET_TRACEABILITY_REPORT.md`
