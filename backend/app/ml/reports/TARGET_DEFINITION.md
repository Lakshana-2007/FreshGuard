# FreshGuard M3 — Remaining Shelf Life (RSL) Target Definitions

## 1. 🍅 Tomato Target Definition
* **Target Name:** `remaining_shelf_life_days`
* **Target Formula:** $\text{RSL} = \text{Total\_Observed\_Shelf\_Life} - \text{Storage\_Duration\_Days}$
* **Failure Endpoint:** Loss of commercial marketability / initiation of fruit fungal decay under ambient storage.
* **Evidence in Raw Data:** `Shelflife_Tomato_NLED_BWC.xlsx` column `shelf-life` (experimentally observed total days to decay for each treatment replicate, ranging from 11 to 35 days).
* **Target Range:** 0.0 to 35.0 days.
* **Observation Distribution:**
  * Total Training Rows: 1,684 daily observations.
  * Zero-RSL Rows: 48 (at day of failure $t = \text{shelf\_life}$).
  * Positive-RSL Rows: 1,636 ($t < \text{shelf\_life}$).
  * Missing Targets: 0.
* **Assumptions & Domain:** Valid for fresh tomatoes stored under ambient room conditions (20–25°C, 65–75% RH) with optional postharvest treatments (Neem dipping / Beeswax coating).

---

## 2. 🥛 Paneer (Dairy) Target Definition
* **Target Name:** `remaining_shelf_life_days`
* **Target Formula:** $\text{RSL} = \max(0.0, 9.0 - \text{Storage\_Duration\_Days})$
* **Failure Endpoint:** Sensory Overall Acceptability score falling below acceptable limit 6.0 (on 9-point hedonic scale).
* **Evidence in Raw Data:** `20241230_Testing_Data.xlsx` sensory score timeline. On Day 9, sensory score drops below 6.0 while microbial counts (TPC) exceed acceptable limits.
* **Target Range:** 0.0 to 9.0 days.
* **Observation Distribution:**
  * Total Training Rows: 50 observations.
  * Zero-RSL Rows: 20 (Days 9, 11, 13, 15).
  * Positive-RSL Rows: 30 (Days 0, 1, 3, 5, 7).
  * Missing Targets: 0.
* **Assumptions & Domain:** Specific to Indian cottage cheese (Paneer) packaged in food-grade LDPE pouches stored under domestic refrigeration (7°C, 37% RH). Does not generalize to arbitrary dairy products.

---

## 3. 🍗 Chicken (Meat / Poultry) Target Definition
* **Target Name:** `remaining_shelf_life_days`
* **Target Formula:** $\text{RSL} = \max(0.0, \text{Spoilage\_Day}(\text{Temp}) - \text{Storage\_Duration\_Days})$
  * For 4°C MAP storage: $\text{Spoilage\_Day} = 7.0$
  * For 8°C MAP storage: $\text{Spoilage\_Day} = 4.0$
  * For 15°C MAP storage: $\text{Spoilage\_Day} = 2.0$
* **Failure Endpoint:** Total Viable Count $\text{TVC} \ge 7.0 \text{ log CFU/g}$ (ICMSF microbiological safety threshold).
* **Evidence in Raw Data:** `Raw data microbial counts.xlsx` column `log_CFU/g LH`. Day at which TVC crosses $7.0 \text{ log CFU/g}$ at 4°C is Day 7.
* **Target Range:** 0.0 to 7.0 days.
* **Observation Distribution:**
  * Total Training Rows: 27 observations.
  * Zero-RSL Rows: 11 ($t \ge \text{Spoilage\_Day}$).
  * Positive-RSL Rows: 16 ($t < \text{Spoilage\_Day}$).
  * Missing Targets: 0.
* **Assumptions & Domain:** Valid for fresh chicken breast fillets stored under MAP (Modified Atmosphere Packaging) at 4°C to 15°C.

---

## 4. 🐟 Seafood (Fish) Target Definition
* **Target Name:** `remaining_shelf_life_days`
* **Target Formula:** $\text{RSL} = \max(0.0, 3.0 - \text{Storage\_Duration\_Days})$
* **Failure Endpoint:** SNI 2729:2013 Organoleptic rejection threshold (< 7.0 score on fish sensory scale).
* **Evidence in Raw Data:** DaFiF experimental session files (`19-01-2024` = Day 1 Fresh, `20-01-2024` = Day 2 Medium, `21-01-2024` = Day 3 Rejection).
* **Target Range:** 0.0 to 2.0 days.
* **Observation Distribution:**
  * Total Training Rows: 6,959 readings.
  * Zero-RSL Rows: 2,561 (Day 3 readings).
  * Positive-RSL Rows: 4,398 (Days 1 & 2 readings).
  * Missing Targets: 0.
* **Assumptions & Domain:** Valid for fresh whole fish (Mackerel, Tilapia, Tuna) stored in flaked ice (0–2°C).

---

## 5. 🥑 Avocado Status
* **Status:** **BLOCKED**
* **Reason:** Raw dataset files are **NOT AVAILABLE LOCALLY**. Target cannot be constructed without local raw data.
