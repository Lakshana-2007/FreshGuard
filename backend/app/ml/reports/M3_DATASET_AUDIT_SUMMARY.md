# FreshGuard M3 — Validated Dataset Audit Summary (Phase 2)

## 1. Executive Summary & Category Audit Matrix

The five candidate food categories were audited against local physical dataset files. No synthetic data, unverified inferences, or fabricated labels were introduced.

| Category | Raw Data Available | Rows | Experimental Units | RSL Target | Leakage Risk | Production Features | Recommended Split | Status |
| :--- | :---: | :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| 🍅 **Tomato** | ✅ YES | 48 | 48 | `RSL = total_days - t` (Direct) | Decay %, Marketability % | Treatment, Temp, Storage Days, Packaging | GroupKFold by `Treatments` | **READY FOR PHASE 3** |
| 🥑 **Avocado** | ❌ NO | 0 | 0 | None (Not constructable) | N/A | N/A | N/A | **RAW DATA NOT AVAILABLE LOCALLY** |
| 🥛 **Paneer / Dairy** | ✅ YES | 99 | 99 | `RSL = 9.0 - t` (Sensory Limit) | Sensory Score | Temp, RH, Storage Days, Packaging | GroupKFold by `Storage_day` | **READY FOR PHASE 3** |
| 🍗 **Chicken / Meat** | ✅ YES | 27 | 27 | `RSL = 7.0 - t` (TVC $\ge 7.0$) | Consumer Accept/Reject | Temp, Storage Days, Packaging | GroupKFold by `Storage_temperature` | **READY FOR PHASE 3** |
| 🐟 **Seafood / Fish** | ✅ YES | 6,948 | 6,948 | `RSL = 3.0 - t` (Sensory Limit) | Organoleptic Score | Temp, Storage Days, Species | GroupKFold by `Species` | **READY FOR PHASE 3** |

---

## 2. Detailed Dataset Audit Reports

### 1. 🍅 Tomato — Dryad Storage & Shelf-Life Dataset
* **Identity:** Dryad Repository (`Shelflife_Tomato_NLED_BWC.xlsx`, `TA_Tomato_NLED_BWC.xlsx`, `TSS_Tomato_NLED_BWC.xlsx`, `WL_Tomato_NLED_BWC.xlsx`, `pH_Tomato_NLED_BWC.xlsx`, `Decay_Tomato_NLED_BWC.xlsx`, `Marketability_Tomato_NLED_BWC.xlsx`, `AA_Tomato_NLED_BWC.xlsx`).
* **Local Location:** `d:\infosys\project 1\dataset\`
* **Data Size:** 8 Excel files, 48 rows per file (4 treatments $\times$ 4 replicates $\times$ 3 neem dipping levels = 48 experimental units).
* **Experimental Unit:** Batch of 4 tomatoes stored under ambient conditions (20–25°C, 65–75% RH).
* **RSL Target Construction:** `remaining_shelf_life_days` is directly observed in `Shelflife_Tomato_NLED_BWC.xlsx` (`shelf-life` column, range 11 to 28 days).
* **Leakage Audit:**
  * **Safe Features:** Treatment combination (Neem Leaf Extract Dipping, Beeswax Coating), replicate index.
  * **Leakage Risk:** `Decay %`, `Marketability %`.
  * **Training-Only Features:** Titratable Acidity (TA), TSS, Ascorbic Acid, pH, Weight Loss %.
* **Production Features:** Storage Temperature (20–25°C), Storage Duration Days, Packaging Type (Uncoated / Beeswax Coated).
* **Recommended Grouping:** GroupKFold on `Treatments` to prevent leakage between treatment replicates.

---

### 2. 🥑 Avocado — Hass Avocado Storage Dataset
* **Identity:** Hass Avocado storage timeline dataset.
* **Local Location:** Not present in local filesystem.
* **Status:** **RAW DATA NOT AVAILABLE LOCALLY**. Per strict execution rules, no synthetic labels or fake rows were generated. This category cannot proceed to ML training without local physical raw data files.

---

### 3. 🥛 Dairy / Paneer — Mendeley Paneer Storage Study
* **Identity:** Mendeley Data Repository (DOI `10.17632/rd9dmr54xx.2`).
* **Local Location:** `d:\infosys\scratch\paneer_data\` (`20241118_DataLog.csv`, `20241230_Testing_Data.xlsx`).
* **Data Size:** 1,950 continuous sensor log rows, 99 longitudinal laboratory quality rows.
* **Experimental Unit:** Paneer sample stored under 7°C, 37% RH in food-grade LDPE pouches.
* **RSL Target Construction:** Documented sensory acceptability limit is Day 9.0 (score falls below cutoff 6.0). Target formula: `RSL = max(0.0, 9.0 - Storage_day)`.
* **Leakage Audit:**
  * **Safe Features:** `Storage_day`, `Temperature` (7°C), `RH` (37%).
  * **Leakage Risk:** `Sensory_Overall_Acceptability`.
  * **Training-Only Features:** Titratable Acidity, Free Fatty Acids, Tyrosine content, TPC log CFU/g.
* **Production Features:** Temperature (7°C), RH (37%), Storage Duration Days, Packaging Type.
* **Recommended Grouping:** GroupKFold on `Storage_day` / batch run.

---

### 4. 🍗 Meat / Poultry — Fresh Chicken Breast MAP Dataset
* **Identity:** Dynamic MAP Chicken Storage Study.
* **Local Location:** Artifact scratch `scratch/round3_data/ds1_chicken/` (`Raw data microbial counts.xlsx`, `Raw data consumer test.xlsx`, `Raw data Microbiota.xlsx`, `Parameters from survival models.xlsx`).
* **Data Size:** 4 Excel files, 27 longitudinal microbial sampling rows, 1,391 consumer sensory test rows, 81 microbiota profiles.
* **Experimental Unit:** Chicken breast fillet in MAP packaging stored under 4°C, 8°C, or 15°C.
* **RSL Target Construction:** Failure threshold is TVC $\ge 7.0 \text{ log CFU/g}$ (ICMSF limit). For 4°C MAP storage, failure occurs at Day 7.0. Target formula: `RSL = max(0.0, 7.0 - Storage_day)`.
* **Leakage Audit:**
  * **Safe Features:** `Storage_day`, `Storage temperature`, `GAS_O2`, `GAS_CO2`.
  * **Leakage Risk:** `Consumer Accept/Reject`.
  * **Training-Only Features:** TVC, Pseudomonas count, Lactic Acid Bacteria, Microbiota relative abundances.
* **Production Features:** Storage Temperature, Storage Duration Days, Packaging Type (MAP).
* **Recommended Grouping:** GroupKFold on `Storage temperature` run.

---

### 5. 🐟 Seafood — DaFiF Fish Freshness Dataset
* **Identity:** DaFiF Fish Freshness Study.
* **Local Location:** Artifact scratch `scratch/dairy_seafood_audit/seafood/` (15 `.xlsx` session files).
* **Data Size:** 15 Excel files, 6,948 total sensor/time reading rows across 3 fish species (Mackerel, Tilapia, Tuna).
* **Experimental Unit:** Individual fish sample stored in 0–2°C ice across 3 storage days (Day 1: Fresh, Day 2: Medium, Day 3: Spoiled).
* **RSL Target Construction:** Rejection point is Day 3.0 under 0–2°C ice storage based on SNI 2729:2013 organoleptic score limit (< 7.0). Target formula: `RSL = max(0.0, 3.0 - Storage_day)`.
* **Leakage Audit:**
  * **Safe Features:** `Species`, `Date`, `Time`, `Storage_day`.
  * **Leakage Risk:** `Organoleptic_Score`.
  * **Training-Only Features:** MQ1 Gas Sensor, TGS1 Gas Sensor.
* **Production Features:** Storage Temperature (0–2°C), Storage Duration Days, Fish Species.
* **Recommended Grouping:** GroupKFold on `Species` / session file.

---

## 3. Strict Scientific Validation Checklist

* ✅ **Row and column counts** derived directly from local physical raw files.
* ✅ **Zero synthetic data** created.
* ✅ **Zero missing values** silently imputed.
* ✅ **Grouping columns** identified to prevent data leakage during train/test splits.
* ✅ **Features separated** into production-available vs. experimental-only laboratory variables.
