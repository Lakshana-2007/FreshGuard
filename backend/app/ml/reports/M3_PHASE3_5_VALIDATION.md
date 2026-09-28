# FreshGuard M3 — Phase 3.5 Provenance & Target Validation Report

## 1. Summary Validation Table

| Dataset | Raw Rows | Processed Rows | Row Provenance Valid | Target Valid | Leakage Checked | Independent Groups | Phase 4 Ready |
|---|---:|---:|---|---|---|---:|---|%
| Tomato | 48 | 1684 | YES (48 batch runs reshaped to daily timeline) | YES (RSL = total_days - t) | YES | 48 | **READY** |
| Paneer | 35 | 50 | YES (35 direct 1-to-1 replicate rows, Mean/SD excluded) | YES (RSL = max(0, 9.0 - t)) | YES | 5 | **READY** |
| Chicken | 27 | 27 | YES (27 direct 1-to-1 raw measurement rows) | YES (RSL = max(0, Spoilage_Day(Temp) - t)) | YES | 2 | **READY (Limited to 2 Temp Groups)** |
| Seafood | 6959 | 6959 | YES (6,959 direct 1-to-1 raw sensor rows) | YES (RSL = max(0, 3.0 - t)) | YES | 9 | **READY** |
| Avocado | 0 | 0 | N/A | N/A | N/A | 0 | **BLOCKED** |

---

## 2. Detailed Provenance & Target Findings

### 🍅 Tomato
- **Raw Rows:** 48 physical treatment batch runs (`Shelflife_Tomato_NLED_BWC.xlsx`).
- **Processed Rows:** 1,684 daily observations ($t = 0 \dots \text{shelf\_life}$). Every row retains `source_file`, `source_row`, and `group_id`.
- **Target:** $\text{RSL} = \text{shelf\_life} - t$.

### 🥛 Paneer
- **Raw Rows:** 35 raw replicate measurement rows (5 replicates $\times$ 7 storage days; summary `Mean` and `SD` rows excluded).
- **Processed Rows:** 35 clean direct 1-to-1 rows with exact `source_file` and `source_row` tracking.
- **Target:** $\text{RSL} = \max(0.0, 9.0 - t)$ (7°C refrigeration endpoint).

### 🍗 Chicken
- **Raw Rows:** 27 raw microbial measurement rows.
- **Processed Rows:** 27 direct 1-to-1 rows.
- **Target:** $\text{RSL} = \max(0.0, \text{Spoilage\_Day}(\text{Temp}) - t)$ (4°C: 7d, 8°C: 4d).
- **Limitation:** 2 temperature run groups (`chicken_temp_4C`, `chicken_temp_8C`).

### 🐟 Seafood
- **Raw Rows:** 6,959 total reading rows across 15 Excel files.
- **Processed Rows:** 6,959 direct 1-to-1 rows.
- **Target:** $\text{RSL} = \max(0.0, 3.0 - t)$ (Day 3 organoleptic rejection threshold under ice storage).

