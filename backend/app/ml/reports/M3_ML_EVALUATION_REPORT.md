# FreshGuard M3 — ML Model Evaluation Report (Phase 4)

## 1. Methodology & Grouped Cross-Validation

To prevent target data leakage, validation was conducted strictly using **Grouped Cross-Validation** based on the independent physical experimental units identified in Phase 3.5:
- **Tomato:** `GroupKFold` across 48 independent treatment-replicate batch groups.
- **Paneer:** `GroupKFold` across 5 independent replicate package groups.
- **Chicken:** `LeaveOneGroupOut` across 2 temperature run groups (`4C` and `8C`).
- **Seafood:** `GroupKFold` across 9 species-date session groups.

## 2. Model Performance Factual Comparison

| Category | Training Rows | Groups | Selected Model | Mean MAE | Mean RMSE | Mean R² | Max Abs Error |
|---|---:|---:|---|---:|---:|---:|---:|
| **Tomato** | 1684 | 48 | `RandomForestRegressor` | **0.2507** | 0.4173 | 0.9983 | 1.16 |
| **Paneer** | 50 | 5 | `LinearRegression` | **0.0000** | 0.0000 | 1.0000 | 0.00 |
| **Chicken** | 27 | 2 | `GradientBoostingRegressor` | **0.7500** | 1.3693 | -0.2143 | 6.00 |
| **Seafood** | 6959 | 9 | `RandomForestRegressor` | **0.0000** | 0.0000 | 1.0000 | 0.00 |
| **Avocado** | 0 | 0 | *BLOCKED* | N/A | N/A | N/A | N/A |

---

## 3. Detailed Category Evaluations

### Tomato Model Evaluation
- **Training Rows:** 1684
- **Independent Group Count:** 48
- **Candidate Comparisons:**
  - `LinearRegression`: MAE = 0.5722 (+/- 0.0591), RMSE = 0.7682, R² = 0.9943
  - `RandomForestRegressor`: MAE = 0.2507 (+/- 0.0396), RMSE = 0.4173, R² = 0.9983
  - `GradientBoostingRegressor`: MAE = 0.3298 (+/- 0.0303), RMSE = 0.4489, R² = 0.9981
- **Selected Model:** `RandomForestRegressor` (Lowest CV MAE)
- **Median Absolute Error:** 0.0810 days
- **Maximum Absolute Error:** 1.1583 days
- **Negative Predictions in OOF:** 0

### Paneer Model Evaluation
- **Training Rows:** 50
- **Independent Group Count:** 5
- **Candidate Comparisons:**
  - `LinearRegression`: MAE = 0.0000 (+/- 0.0000), RMSE = 0.0000, R² = 1.0000
  - `RandomForestRegressor`: MAE = 0.0150 (+/- 0.0000), RMSE = 0.0170, R² = 1.0000
  - `GradientBoostingRegressor`: MAE = 0.0001 (+/- 0.0000), RMSE = 0.0001, R² = 1.0000
- **Selected Model:** `LinearRegression` (Lowest CV MAE)
- **Median Absolute Error:** 0.0000 days
- **Maximum Absolute Error:** 0.0000 days
- **Negative Predictions in OOF:** 0

### Chicken Model Evaluation
- **Training Rows:** 27
- **Independent Group Count:** 2
- **Candidate Comparisons:**
  - `LinearRegression`: MAE = 1.5805 (+/- 0.0805), RMSE = 2.2405, R² = -0.2143
  - `RandomForestRegressor`: MAE = 0.7700 (+/- 0.7300), RMSE = 1.4039, R² = -0.2143
  - `GradientBoostingRegressor`: MAE = 0.7500 (+/- 0.7500), RMSE = 1.3693, R² = -0.2143
- **Selected Model:** `GradientBoostingRegressor` (Lowest CV MAE)
- **Median Absolute Error:** 0.0000 days
- **Maximum Absolute Error:** 6.0000 days
- **Negative Predictions in OOF:** 0
- **Evaluation Limitation Note:** *MODEL SELECTION UNCERTAIN DUE TO LIMITED INDEPENDENT EXPERIMENTAL GROUPS (2 groups).* High metric variance expected.

### Seafood Model Evaluation
- **Training Rows:** 6959
- **Independent Group Count:** 9
- **Candidate Comparisons:**
  - `LinearRegression`: MAE = 0.0000 (+/- 0.0000), RMSE = 0.0000, R² = 0.6000
  - `RandomForestRegressor`: MAE = 0.0000 (+/- 0.0000), RMSE = 0.0000, R² = 1.0000
  - `GradientBoostingRegressor`: MAE = 0.0000 (+/- 0.0000), RMSE = 0.0000, R² = 0.6000
- **Selected Model:** `RandomForestRegressor` (Lowest CV MAE)
- **Median Absolute Error:** 0.0000 days
- **Maximum Absolute Error:** 0.0000 days
- **Negative Predictions in OOF:** 0

