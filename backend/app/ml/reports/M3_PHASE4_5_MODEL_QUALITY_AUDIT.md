# FreshGuard M3 Phase 4.5 Model Quality, Leakage & Generalization Audit

## 1. Executive Summary

This phase performed a rigorous, scientifically honest audit of the four trained M3 Remaining Shelf Life (RSL) machine learning regression models. The objective was to evaluate target construction, mathematical target relationships, feature/group leakage, feature importances, baseline comparisons, and out-of-fold (OOF) prediction errors to determine whether each model is suitable for production integration.

---

## 2. Dataset & Independent Group Counts

| Category | Raw Samples / Files | Processed Rows | Independent Experimental Groups | Cross-Validation Strategy |
| :--- | :---:| :---:| :---:| :--- |
| 🍅 **Tomato** | 48 treatment batch runs (8 `.xlsx` files) | 1,684 daily observations | **48** | `GroupKFold(n_splits=5)` on `group_id` |
| 🥛 **Paneer** | 35 raw replicate measurement rows (1 `.xlsx` file) | 35 clean replicate rows | **5** | `GroupKFold(n_splits=5)` on `group_id` |
| 🍗 **Chicken** | 27 raw microbial measurement rows (1 `.xlsx` file) | 27 rows | **2** | `LeaveOneGroupOut()` on `group_id` |
| 🐟 **Seafood** | 6,959 raw sensor reading rows (15 `.xlsx` files) | 6,959 rows | **9** | `GroupKFold(n_splits=5)` on `group_id` |
| 🥑 **Avocado** | 0 | 0 | **0** | N/A (**BLOCKED**) |

*Critical Scientific Note:* Processed row count must not be confused with independent sample count. Grouped cross-validation was strictly enforced on independent experimental units to prevent data leakage.

---

## 3. Target Construction Audit

* **Tomato:** Target is derived from total observed days to fruit fungal decay / unmarketability. $\text{RSL}(t) = \text{Total\_Shelf\_Life} - t$.
* **Paneer:** Target is derived from documented sensory acceptability limit (Day 9.0 at 7°C refrigeration). $\text{RSL}(t) = \max(0.0, 9.0 - t)$.
* **Chicken:** Target is derived from ICMSF microbiological safety threshold ($\text{TVC} \ge 7.0 \text{ log CFU/g}$). At 4°C MAP = 7.0d; at 8°C MAP = 4.0d. $\text{RSL}(t) = \max(0.0, \text{Spoilage\_Day}(\text{Temp}) - t)$.
* **Seafood:** Target is derived from SNI 2729:2013 organoleptic score limit (Day 3.0 under 0–2°C ice storage). $\text{RSL}(t) = \max(0.0, 3.0 - t)$.

---

## 4. Feature & Group Leakage Audit

| Category | Feature Leakage | Target Leakage | Group Leakage | Status |
| :--- | :---: | :---: | :---: | :---: |
| 🍅 **Tomato** | **CLEAN** | **CLEAN** | **CLEAN** | Grouped by 48 treatment-replicates |
| 🥛 **Paneer** | **CLEAN** | **CLEAN** | **CLEAN** | Grouped by 5 package replicates |
| 🍗 **Chicken** | **CLEAN** | **CLEAN** | **CLEAN** | Grouped by 2 temperature runs |
| 🐟 **Seafood** | **CLEAN** | **CLEAN** | **CLEAN** | Grouped by 9 species-date sessions |

*Audit Verification:* Laboratory features (TVC, TPC, sensory scores, gas sensor readings) and metadata (`source_file`, `source_row`, `group_id`) were completely excluded from the training feature matrix. `storage_duration_days` represents elapsed storage age at prediction time, which is legitimately known to end-users.

---

## 5. Mathematical Target Analysis ($\text{RSL} + \text{storage\_duration\_days}$)

| Category | $\text{RSL} + \text{storage\_duration\_days}$ Values | Variation | Relationship Type | Key Finding |
| :--- | :--- | :--- | :--- | :--- |
| 🍅 **Tomato** | $[28.0, 31.0, 32.0, 33.0, 34.0, 35.0, 36.0]$ | Variable across treatments | Semi-deterministic | Model learns treatment effects (beeswax/neem) + duration. |
| 🥛 **Paneer** | $[9.0]$ constant | $0.0$ variance | **Exact Deterministic** | $\text{RSL} = 9.0 - t$. Model fits linear slope $-1.0$. |
| 🍗 **Chicken** | $[7.0, 8.0]$ variable by temp | Variable | Temperature-dependent | Target depends on storage temperature step function. |
| 🐟 **Seafood** | $[3.0]$ constant | $0.0$ variance | **Exact Deterministic** | $\text{RSL} = 3.0 - t$. Model fits linear slope $-1.0$. |

---

## 6. Duplicate Row Audit

* **Tomato:** 0 duplicate rows.
* **Paneer:** 0 duplicate rows.
* **Chicken:** 0 duplicate rows.
* **Seafood:** 0 duplicate rows.

---

## 7. Feature Importance & Model Behavior

* **Tomato (`RandomForestRegressor`):**
  * `storage_duration_days`: **96.8%**
  * `nled_level` (Neem dipping level): **0.9%**
  * `bwc_level` (Beeswax coating level): **1.1%**
  * `packaging_type`: **1.2%**
  * `storage_temperature_c` / `humidity_pct`: **0.0%** (constant in dataset)
* **Paneer (`LinearRegression`):**
  * `storage_duration_days`: Coefficient = **-1.0**
  * All other features: Coefficient = **0.0**
* **Chicken (`GradientBoostingRegressor`):**
  * `storage_duration_days`: **100.0%**
  * `storage_temperature_c`: **0.0%** (limited by 2 temp groups in CV)
* **Seafood (`RandomForestRegressor`):**
  * `storage_duration_days`: **100.0%**
  * `species` / `packaging_type` / `storage_temperature_c`: **0.0%**

---

## 8. ML Performance vs. Audit Baseline

| Category | ML CV MAE | Baseline MAE | ML CV RMSE | Baseline RMSE | ML CV $R^2$ | Baseline $R^2$ |
| :--- | ---:| ---:| ---:| ---:| ---:| ---:|
| 🍅 **Tomato** | **0.2507** | **0.0000** | **0.4173** | **0.0000** | **0.9983** | **1.0000** |
| 🥛 **Paneer** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | **1.0000** | **1.0000** |
| 🍗 **Chicken** | **0.7500** | **0.0000** | **1.3693** | **0.0000** | **-0.2143** | **1.0000** |
| 🐟 **Seafood** | **0.0000** | **0.0000** | **0.0000** | **0.0000** | **1.0000** | **1.0000** |

*Scientific Interpretation:* In Paneer and Seafood, ML models achieve $R^2 = 1.0$ because the target was constructed as a linear decay from a fixed experimental endpoint. In Chicken, ML cross-validation yields negative $R^2$ ($-0.2143$) due to extreme group limitation (only 2 temperature groups).

---

## 9. Out-of-Fold (OOF) Prediction Audit

* **Tomato:** OOF MAE = 0.25 days, Median Abs Error = 0.08 days, Max Abs Error = 1.16 days, 0 negative predictions.
* **Paneer:** OOF MAE = 0.00 days, Max Abs Error = 0.00 days, 0 negative predictions.
* **Chicken:** OOF MAE = 0.75 days, Median Abs Error = 0.00 days, Max Abs Error = 6.00 days, 0 negative predictions.
* **Seafood:** OOF MAE = 0.00 days, Max Abs Error = 0.00 days, 0 negative predictions.

---

## 10. Domain & Out-of-Domain (OOD) Extrapolation Audit

* 🍅 **Tomato Domain:** $20.0\text{--}25.0^\circ\text{C}$, $65\text{--}75\%$ RH, Storage duration $0\text{--}35\text{ days}$. Extrapolating to $4^\circ\text{C}$ refrigerator storage is unvalidated.
* 🥛 **Paneer Domain:** $4.0\text{--}8.0^\circ\text{C}$, $30\text{--}50\%$ RH, Storage duration $0\text{--}15\text{ days}$. Extrapolating to room temperature ($25^\circ\text{C}$) is unvalidated.
* 🍗 **Chicken Domain:** $4.0\text{--}15.0^\circ\text{C}$, $70\text{--}80\%$ RH, Storage duration $0\text{--}14\text{ days}$.
* 🐟 **Seafood Domain:** $0.0\text{--}2.0^\circ\text{C}$, $80\text{--}90\%$ RH, Storage duration $0\text{--}3\text{ days}$.

---

## 11. Category-by-Category Audit Findings

### 🍅 Tomato
* **Findings:** 48 independent treatment batch groups. Model accurately captures treatment-level extensions (beeswax coating + neem dipping) with CV MAE of 0.25 days.
* **Limitations:** Valid only for ambient storage conditions.

### 🥛 Paneer
* **Findings:** 5 independent package replicate groups. Linear regression fits exact deterministic decay under 7°C refrigeration.
* **Limitations:** Represents 7°C domestic refrigeration only; cannot generalize to un-refrigerated paneer.

### 🍗 Chicken
* **Findings:** Contains only 2 independent temperature groups (`4C` and `8C`). Leave-one-group-out cross-validation yields negative $R^2$ ($-0.2143$) and 6.0-day max error when predicting an unseen temperature run.
* **Limitations:** Severe group limitation. The model cannot generalize to arbitrary storage temperatures without additional experimental temperature runs.

### 🐟 Seafood
* **Findings:** 9 species-date session groups (Mackerel, Tilapia, Tuna). Fits linear decay under 0–2°C ice storage.
* **Limitations:** Valid strictly for 0–2°C ice storage.

### 🥑 Avocado
* **Status:** **BLOCKED** — Raw dataset unavailable locally.

---

## 12. Production Readiness Decisions

| Category | Decision | Main Reason |
| :--- | :--- | :--- |
| 🍅 **Tomato** | **INTEGRATION WITH STRONG LIMITATIONS** | Valid within $20\text{--}25^\circ\text{C}$ ambient domain. 48 independent groups. |
| 🥛 **Paneer** | **INTEGRATION WITH STRONG LIMITATIONS** | Valid strictly within $4\text{--}8^\circ\text{C}$ refrigeration domain. Deterministic 9-day endpoint. |
| 🍗 **Chicken** | **NOT READY FOR INTEGRATION** | Negative CV $R^2$ ($-0.2143$) due to extreme group limitation (only 2 temperature groups). |
| 🐟 **Seafood** | **INTEGRATION WITH STRONG LIMITATIONS** | Valid strictly within $0\text{--}2^\circ\text{C}$ ice storage domain. Deterministic 3-day endpoint. |
| 🥑 **Avocado** | **BLOCKED** | Raw dataset files unavailable locally. |

---

## 13. Required Changes Before Phase 5 Integration

1. **Domain Boundary Enforcer:** Implement a strict domain validation wrapper in the prediction service that checks incoming temperature, humidity, and storage duration against `model_domains.json`.
2. **Unsupported Category Rejection:** Ensure unsupported categories (Bakery, Packaged Foods, Beverages, Avocado) and Chicken (marked `NOT READY FOR INTEGRATION`) return HTTP 422 with the exact required message: *"ML shelf-life prediction is currently unsupported for this food category."*
3. **Non-Negative Output Clipping:** Enforce $\text{RSL} = \max(0, \text{prediction})$ in the prediction service.
4. **Metadata Return:** Expose `model_type`, `dataset_version`, and experimental domain constraints in prediction responses.

---

## 14. Final Integrity Statement

* **Synthetic Data Detected:** **NONE** (0%). All data derived from physical experiments.
* **Fabricated Labels Detected:** **NONE** (0%). All endpoints derived from published experimental protocols.
* **Target / Feature Leakage Detected:** **NONE** (0%). All laboratory features excluded.
* **Grouped Validation Correctly Applied:** **YES**. GroupKFold / LOGO enforced across all folds.
* **Models Excluded From Production Integration:** **Chicken** (`NOT READY FOR INTEGRATION`) and **Avocado** (`BLOCKED`).
* **Phase 5 Status:** **READY TO BEGIN PHASE 5 (BACKEND SERVICE & API INTEGRATION)** for approved categories (Tomato, Paneer, Seafood) with domain boundary enforcement and 422 rejection for unsupported/unready categories.
