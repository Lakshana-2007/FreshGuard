# FreshGuard M3 — Synthetic Dataset and Model Extension Report

## 1. Executive Summary & Disclaimer

> **STATUS**: **DEMONSTRATION / EXTENSION ONLY**
> 
> **IMPORTANT NOTICE**: This document describes the synthetic datasets, generation algorithms, and demonstration machine learning models created to extend FreshGuard M3 remaining shelf life (RSL) inference to 5 non-validated food categories (Vegetables, Meat & Poultry, Bakery Products, Packaged Foods, Beverages). **NONE OF THE SYNTHETIC OBSERVATIONS HERE REPRESENT REAL-WORLD LABORATORY MEASUREMENTS.** Existing production models (Tomato, Paneer, Seafood) remain completely unchanged and rely strictly on real/traceable datasets.

## 2. Category Summary Table

| Category | Dataset Type | Total Rows | Train / Test | Test MAE (days) | Test RMSE | Test R² | 5-Fold CV MAE | Model Artifact |
|---|---|---|---|---|---|---|---|---|
| **vegetables** | `SYNTHETIC` | 1200 | 960 / 240 | 0.363 | 0.537 | 0.972 | 0.363 | `vegetables_rsl_synthetic.joblib` |
| **meat_poultry** | `SYNTHETIC` | 1200 | 960 / 240 | 0.257 | 0.376 | 0.966 | 0.268 | `meat_poultry_rsl_synthetic.joblib` |
| **bakery** | `SYNTHETIC` | 1200 | 960 / 240 | 0.229 | 0.388 | 0.951 | 0.234 | `bakery_rsl_synthetic.joblib` |
| **packaged_foods** | `SYNTHETIC` | 1200 | 960 / 240 | 0.598 | 0.79 | 0.987 | 0.554 | `packaged_foods_rsl_synthetic.joblib` |
| **beverages** | `SYNTHETIC` | 1200 | 960 / 240 | 0.329 | 0.501 | 0.983 | 0.361 | `beverages_rsl_synthetic.joblib` |

---

## 3. Detailed Category Specifications

### Category: Vegetables
- **1. Category Name**: `vegetables`
- **2. Dataset Type**: `DATA_TYPE = SYNTHETIC`
- **3. Number of Rows**: 1200 synthetic records
- **4. Feature Definitions**:
  - `product_type`: Specific product variety within category
  - `storage_temperature_c`: Storage temperature in degrees Celsius
  - `humidity_pct`: Relative storage humidity percentage
  - `storage_duration_days`: Days elapsed in storage
  - `packaging_type`: Packaging enclosure type (perforated, sealed, open)
  - `remaining_shelf_life_days` (Target): Estimated days of acceptable quality remaining
- **5. Feature Ranges / Domain Bounds**:
  - Temperature: 2.0°C to 12.0°C
  - Humidity: 80.0% to 98.0%
  - Storage Duration: 0.0 to 14.0 days
  - Allowed Packaging: `perforated, sealed, open`
- **6. Synthetic Generation Formula & Logic**: `base_sl=12.0d at optimal (4°C, 95% RH), temp_penalty=(T-4)*0.70, rh_penalty=|RH-95|*0.15, packaging modifiers (sealed:+1.0, open:-2.0, perforated:0), RSL = max(0, initial_sl - duration + N(0, 0.45)).`
- **7. Controlled Noise Assumptions**: Gaussian distributed noise $\mathcal{N}(0, \sigma^2)$ added to RSL to simulate natural biological variability.
- **8. Model Used**: `RandomForestRegressor(n_estimators=100, random_state=42)`
- **9. Evaluation Metrics**:
  - Holdout Test MAE: **0.363 days**
  - Holdout Test RMSE: **0.537 days**
  - Holdout Test R²: **0.972**
  - 5-Fold GroupKFold Cross-Validation MAE: **0.363 days**
- **10. Metrics Explanation**: R² scores are high (~0.95–0.98) because synthetic data is governed by underlying mathematical kinetics with controlled Gaussian noise. This is an expected artifact of synthetic simulation.
- **11. Limitations & Non-Validation Statement**: This model reflects the specified mathematical equations rather than complex biochemical pathways (enzymatic browning, microbial proliferation curves, atmospheric respiration rates). **It must NEVER be treated as real-world clinical or agricultural validation.**

### Category: Meat Poultry
- **1. Category Name**: `meat_poultry`
- **2. Dataset Type**: `DATA_TYPE = SYNTHETIC`
- **3. Number of Rows**: 1200 synthetic records
- **4. Feature Definitions**:
  - `product_type`: Specific product variety within category
  - `storage_temperature_c`: Storage temperature in degrees Celsius
  - `humidity_pct`: Relative storage humidity percentage
  - `storage_duration_days`: Days elapsed in storage
  - `packaging_type`: Packaging enclosure type (modified_atmosphere, vacuum_sealed, airtight, open)
  - `remaining_shelf_life_days` (Target): Estimated days of acceptable quality remaining
- **5. Feature Ranges / Domain Bounds**:
  - Temperature: 0.0°C to 8.0°C
  - Humidity: 65.0% to 85.0%
  - Storage Duration: 0.0 to 8.0 days
  - Allowed Packaging: `modified_atmosphere, vacuum_sealed, airtight, open`
- **6. Synthetic Generation Formula & Logic**: `base_sl=7.0d at optimal (1°C, 75% RH), temp_penalty=(T-1)*0.90, rh_penalty=|RH-75|*0.05, packaging modifiers (vac:+2.0, map:+1.5, airtight:+0.5, open:-1.5), RSL = max(0, initial_sl - duration + N(0, 0.35)).`
- **7. Controlled Noise Assumptions**: Gaussian distributed noise $\mathcal{N}(0, \sigma^2)$ added to RSL to simulate natural biological variability.
- **8. Model Used**: `RandomForestRegressor(n_estimators=100, random_state=42)`
- **9. Evaluation Metrics**:
  - Holdout Test MAE: **0.257 days**
  - Holdout Test RMSE: **0.376 days**
  - Holdout Test R²: **0.966**
  - 5-Fold GroupKFold Cross-Validation MAE: **0.268 days**
- **10. Metrics Explanation**: R² scores are high (~0.95–0.98) because synthetic data is governed by underlying mathematical kinetics with controlled Gaussian noise. This is an expected artifact of synthetic simulation.
- **11. Limitations & Non-Validation Statement**: This model reflects the specified mathematical equations rather than complex biochemical pathways (enzymatic browning, microbial proliferation curves, atmospheric respiration rates). **It must NEVER be treated as real-world clinical or agricultural validation.**

### Category: Bakery
- **1. Category Name**: `bakery`
- **2. Dataset Type**: `DATA_TYPE = SYNTHETIC`
- **3. Number of Rows**: 1200 synthetic records
- **4. Feature Definitions**:
  - `product_type`: Specific product variety within category
  - `storage_temperature_c`: Storage temperature in degrees Celsius
  - `humidity_pct`: Relative storage humidity percentage
  - `storage_duration_days`: Days elapsed in storage
  - `packaging_type`: Packaging enclosure type (paper, sealed, airtight, open)
  - `remaining_shelf_life_days` (Target): Estimated days of acceptable quality remaining
- **5. Feature Ranges / Domain Bounds**:
  - Temperature: 15.0°C to 30.0°C
  - Humidity: 40.0% to 75.0%
  - Storage Duration: 0.0 to 10.0 days
  - Allowed Packaging: `paper, sealed, airtight, open`
- **6. Synthetic Generation Formula & Logic**: `base_sl=7.0d at ambient (20°C, 50% RH), temp_penalty=max(0, T-20)*0.35, rh_penalty=|RH-50|*0.10, packaging modifiers (airtight:+0.8, sealed:+0.5, paper:-0.5, open:-2.0), RSL = max(0, initial_sl - duration + N(0, 0.40)).`
- **7. Controlled Noise Assumptions**: Gaussian distributed noise $\mathcal{N}(0, \sigma^2)$ added to RSL to simulate natural biological variability.
- **8. Model Used**: `RandomForestRegressor(n_estimators=100, random_state=42)`
- **9. Evaluation Metrics**:
  - Holdout Test MAE: **0.229 days**
  - Holdout Test RMSE: **0.388 days**
  - Holdout Test R²: **0.951**
  - 5-Fold GroupKFold Cross-Validation MAE: **0.234 days**
- **10. Metrics Explanation**: R² scores are high (~0.95–0.98) because synthetic data is governed by underlying mathematical kinetics with controlled Gaussian noise. This is an expected artifact of synthetic simulation.
- **11. Limitations & Non-Validation Statement**: This model reflects the specified mathematical equations rather than complex biochemical pathways (enzymatic browning, microbial proliferation curves, atmospheric respiration rates). **It must NEVER be treated as real-world clinical or agricultural validation.**

### Category: Packaged Foods
- **1. Category Name**: `packaged_foods`
- **2. Dataset Type**: `DATA_TYPE = SYNTHETIC`
- **3. Number of Rows**: 1200 synthetic records
- **4. Feature Definitions**:
  - `product_type`: Specific product variety within category
  - `storage_temperature_c`: Storage temperature in degrees Celsius
  - `humidity_pct`: Relative storage humidity percentage
  - `storage_duration_days`: Days elapsed in storage
  - `packaging_type`: Packaging enclosure type (modified_atmosphere, sealed, vacuum_sealed)
  - `remaining_shelf_life_days` (Target): Estimated days of acceptable quality remaining
- **5. Feature Ranges / Domain Bounds**:
  - Temperature: 2.0°C to 10.0°C
  - Humidity: 45.0% to 70.0%
  - Storage Duration: 0.0 to 25.0 days
  - Allowed Packaging: `modified_atmosphere, sealed, vacuum_sealed`
- **6. Synthetic Generation Formula & Logic**: `base_sl=21.0d at refrigerated optimal (4°C, 55% RH), temp_penalty=(T-4)*1.10, rh_penalty=|RH-55|*0.04, packaging modifiers (vac:+4.0, map:+3.0, sealed:0), RSL = max(0, initial_sl - duration + N(0, 0.60)).`
- **7. Controlled Noise Assumptions**: Gaussian distributed noise $\mathcal{N}(0, \sigma^2)$ added to RSL to simulate natural biological variability.
- **8. Model Used**: `RandomForestRegressor(n_estimators=100, random_state=42)`
- **9. Evaluation Metrics**:
  - Holdout Test MAE: **0.598 days**
  - Holdout Test RMSE: **0.79 days**
  - Holdout Test R²: **0.987**
  - 5-Fold GroupKFold Cross-Validation MAE: **0.554 days**
- **10. Metrics Explanation**: R² scores are high (~0.95–0.98) because synthetic data is governed by underlying mathematical kinetics with controlled Gaussian noise. This is an expected artifact of synthetic simulation.
- **11. Limitations & Non-Validation Statement**: This model reflects the specified mathematical equations rather than complex biochemical pathways (enzymatic browning, microbial proliferation curves, atmospheric respiration rates). **It must NEVER be treated as real-world clinical or agricultural validation.**

### Category: Beverages
- **1. Category Name**: `beverages`
- **2. Dataset Type**: `DATA_TYPE = SYNTHETIC`
- **3. Number of Rows**: 1200 synthetic records
- **4. Feature Definitions**:
  - `product_type`: Specific product variety within category
  - `storage_temperature_c`: Storage temperature in degrees Celsius
  - `humidity_pct`: Relative storage humidity percentage
  - `storage_duration_days`: Days elapsed in storage
  - `packaging_type`: Packaging enclosure type (airtight, sealed, open)
  - `remaining_shelf_life_days` (Target): Estimated days of acceptable quality remaining
- **5. Feature Ranges / Domain Bounds**:
  - Temperature: 2.0°C to 10.0°C
  - Humidity: 40.0% to 70.0%
  - Storage Duration: 0.0 to 18.0 days
  - Allowed Packaging: `airtight, sealed, open`
- **6. Synthetic Generation Formula & Logic**: `base_sl=14.0d at chilled optimal (4°C, 50% RH), temp_penalty=(T-4)*0.95, rh_penalty=|RH-50|*0.02, packaging modifiers (airtight:+1.0, sealed:0, open:-5.0), RSL = max(0, initial_sl - duration + N(0, 0.50)).`
- **7. Controlled Noise Assumptions**: Gaussian distributed noise $\mathcal{N}(0, \sigma^2)$ added to RSL to simulate natural biological variability.
- **8. Model Used**: `RandomForestRegressor(n_estimators=100, random_state=42)`
- **9. Evaluation Metrics**:
  - Holdout Test MAE: **0.329 days**
  - Holdout Test RMSE: **0.501 days**
  - Holdout Test R²: **0.983**
  - 5-Fold GroupKFold Cross-Validation MAE: **0.361 days**
- **10. Metrics Explanation**: R² scores are high (~0.95–0.98) because synthetic data is governed by underlying mathematical kinetics with controlled Gaussian noise. This is an expected artifact of synthetic simulation.
- **11. Limitations & Non-Validation Statement**: This model reflects the specified mathematical equations rather than complex biochemical pathways (enzymatic browning, microbial proliferation curves, atmospheric respiration rates). **It must NEVER be treated as real-world clinical or agricultural validation.**

## 4. Production vs Synthetic Model Registry Comparison

| Category | Provenance | Model Type | Registry Status | Target Metric Validation |
|---|---|---|---|---|
| **Tomato** | Real / Traceable | RandomForestRegressor | Production Active | Real Experimental (CV MAE 0.25d) |
| **Paneer** | Real / Traceable | LinearRegression | Production Active | Real Experimental (CV MAE 0.00d) |
| **Seafood** | Real / Traceable | RandomForestRegressor | Production Active | Real Experimental (CV MAE 0.00d) |
| **Vegetables** | Synthetic | RandomForestRegressor | Synthetic Extension | Synthetic Formula (CV MAE 0.38d) |
| **Meat & Poultry** | Synthetic | RandomForestRegressor | Synthetic Extension | Synthetic Formula (CV MAE 0.30d) |
| **Bakery** | Synthetic | RandomForestRegressor | Synthetic Extension | Synthetic Formula (CV MAE 0.32d) |
| **Packaged Foods** | Synthetic | RandomForestRegressor | Synthetic Extension | Synthetic Formula (CV MAE 0.49d) |
| **Beverages** | Synthetic | RandomForestRegressor | Synthetic Extension | Synthetic Formula (CV MAE 0.40d) |

Generated on: 2026-09-27 16:14:18 UTC
