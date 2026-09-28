# FreshGuard M3 — Target Validation Report (Phase 3)

## 1. Processed Training Dataset Validation Table

| Dataset | Raw Rows | Training Rows | Target | Min RSL | Max RSL | Groups | Production Features | Status |
|---|---:|---:|---|---:|---:|---:|---|---|
| Tomato | 48 | 1684 | `remaining_shelf_life_days` | 0.0 | 36.0 | 48 | nled_level, bwc_level, temp, humidity, duration, packaging | **READY FOR ML** |
| Paneer | 36 | 50 | `remaining_shelf_life_days` | 0.0 | 9.0 | 5 | temp, humidity, duration, packaging | **READY FOR ML** |
| Chicken | 27 | 27 | `remaining_shelf_life_days` | 0.0 | 6.0 | 2 | temp, humidity, duration, packaging | **READY FOR ML** |
| Seafood | 6948 | 6959 | `remaining_shelf_life_days` | 0.0 | 2.0 | 9 | species, temp, humidity, duration, packaging | **READY FOR ML** |
| Avocado | 0 | 0 | None | N/A | N/A | 0 | N/A | **BLOCKED** |

---

## 2. Target Derivation & Leakage Prevention Rules

### Tomato
- **Formula:** `RSL = total_observed_shelf_life - storage_duration_days`
- **Leakage Removed:** Total shelf life column, decay %, marketability %.
- **Group ID:** `group_id = 'tomato_' + treatment + '_rep' + rep`

### Paneer
- **Formula:** `RSL = max(0.0, 9.0 - storage_duration_days)` (7°C domestic refrigeration)
- **Leakage Removed:** Sensory overall acceptability scores.
- **Group ID:** `group_id = 'paneer_repl' + repl`

### Chicken
- **Formula:** `RSL = max(0.0, Spoilage_Day(Temp) - storage_duration_days)` (4°C: 7d, 8°C: 4d, 15°C: 2d)
- **Leakage Removed:** Consumer accept/reject sensory scores.
- **Group ID:** `group_id = 'chicken_temp_' + temp`

### Seafood
- **Formula:** `RSL = max(0.0, 3.0 - storage_duration_days)` (0-2°C ice storage)
- **Leakage Removed:** Organoleptic score limit.
- **Group ID:** `group_id = 'seafood_' + species + '_' + date`

