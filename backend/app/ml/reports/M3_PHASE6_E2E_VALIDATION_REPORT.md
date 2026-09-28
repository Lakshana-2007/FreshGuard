# FreshGuard M3 Phase 6 — End-to-End Validation Report

## 1. Environment

| Item | Value |
|------|-------|
| **Project Root** | `D:\infosys\project 1\` |
| **Backend Virtual Environment** | `D:\infosys\project 1\backend\.venv\Scripts\python.exe` (Python 3.10.0) |
| **Backend Server** | `http://127.0.0.1:8000` (uvicorn `app.main:app`) |
| **Frontend Server** | `http://localhost:5173` (Vite) |
| **Database** | PostgreSQL at `localhost:5432/freshness_db` |
| **DATABASE_URL** | `postgresql+psycopg://postgres:laks9344773283@localhost:5432/freshness_db` |
| **Validation Timestamp** | 2026-09-25T08:50:38+05:30 |
| **Execution Tooling** | Direct Python HTTP E2E Harness (`tmp_phase6_http_e2e.py`) & Subsystem Suites |

---

## 2. Backend Startup

**Command:**
```powershell
Start-Process -FilePath "d:\infosys\project 1\backend\.venv\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory "d:\infosys\project 1\backend"
```

**Startup Result:**
- Startup Log:
  ```text
  INFO:     Started server process [25036]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
  ```
- `GET /health` → **HTTP 200 OK**
  ```json
  {"status":"ok","service":"food-freshness-api","ml_available":true,"model_status":"ready"}
  ```
- **Verification:**
  - Application starts cleanly: PASS
  - No import errors: PASS
  - No model loading errors: PASS (All 3 production models `tomato_rsl.joblib`, `paneer_rsl.joblib`, `seafood_rsl.joblib` loaded)
  - No database errors: PASS
- **Status: PASS**

---

## 3. Frontend Startup / Build

**Command:**
```bash
npm run build # (in d:\infosys\project 1\frontend)
```

**Build Output:**
```text
> food-freshness-milestone1@1.0.0 build
> vite build

vite v7.3.6 building client environment for production...
transforming...
✓ 1580 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.42 kB │ gzip:  0.29 kB
dist/assets/index-C7rNhJ3A.css   31.91 kB │ gzip:  6.26 kB
dist/assets/index-CbypSGVU.js   246.52 kB │ gzip: 75.39 kB
✓ built in 13.83s
```

- **Verification:**
  - Frontend production build succeeds: PASS
  - M3 components compile without fatal build errors: PASS
  - No redesign performed: PASS
- **Status: PASS**

---

## 4. Authentication

**Flow Executed via Real HTTP Requests:**
1. `POST /auth/register` (New user: `role="food_quality_inspector"`) → **HTTP 201 Created**, returned `access_token`
2. `POST /auth/login` (Same user credentials) → **HTTP 200 OK**, returned `access_token`
3. `GET /auth/me` with Bearer JWT → **HTTP 200 OK**, returned user profile (`id`, `email`, `role`, `full_name`)
4. Unauthenticated checks:
   - `POST /m3/shelf-life/predict` without JWT → **HTTP 401 Unauthorized**
   - `POST /m3/shelf-life/predict` with invalid JWT → **HTTP 401 Unauthorized**
   - `GET /m3/shelf-life/history` without JWT → **HTTP 401 Unauthorized**
   - `GET /m3/analytics` without JWT → **HTTP 401 Unauthorized**
- **Status: PASS**

---

## 5. Tomato E2E

**Request:** `POST /m3/shelf-life/predict`
```json
{
  "food_type": "tomato",
  "temperature_c": 22.5,
  "humidity_pct": 70.0,
  "storage_duration_days": 2,
  "packaging_type": "uncoated",
  "nled_level": 0,
  "bwc_level": 0
}
```

**Actual Response:** **HTTP 201 Created**
```json
{
  "id": 81,
  "food_type": "tomato",
  "remaining_shelf_life_days": 26,
  "predicted_expiry_date": "2026-10-21",
  "confidence": null,
  "risk_level": "low",
  "official_freshness_score": 75,
  "score_components": {
    "visual_condition_score": 70,
    "storage_condition_score": 83,
    "shelf_life_score": 74,
    "product_age_score": 100
  },
  "storage_impact": {
    "temperature_score": 100.0,
    "humidity_score": 100.0,
    "condition_score": 83.0
  },
  "storage_compliance": "compliant",
  "recommendations": [
    {
      "priority": "low",
      "action": "Maintain current storage conditions",
      "reason": "Storage conditions are optimal for tomato."
    },
    {
      "priority": "low",
      "action": "Standard FEFO rotation",
      "reason": "Sufficient shelf life remaining (26 days)."
    }
  ],
  "model_type": "ML_RandomForestRegressor",
  "created_at": "2026-09-25T03:19:26.230876Z"
}
```

- **Verification:**
  - HTTP success: PASS (HTTP 201)
  - Predicted shelf life exists & >= 0: PASS (26 days)
  - Confidence is null: PASS (`null`)
  - Correct model is `tomato_rsl.joblib` (`ML_RandomForestRegressor`): PASS
  - Database record created: PASS (ID 81 in `shelf_life_predictions`)
- **Status: PASS**

---

## 6. Paneer E2E

**Request:** `POST /m3/shelf-life/predict`
```json
{
  "food_type": "paneer",
  "temperature_c": 7.0,
  "humidity_pct": 37.0,
  "storage_duration_days": 2,
  "packaging_type": "sealed"
}
```

**Actual Response:** **HTTP 201 Created**
```json
{
  "id": 84,
  "food_type": "paneer",
  "remaining_shelf_life_days": 7,
  "predicted_expiry_date": "2026-10-02",
  "confidence": null,
  "risk_level": "moderate",
  "official_freshness_score": 57,
  "score_components": {
    "visual_condition_score": 70,
    "storage_condition_score": 58,
    "shelf_life_score": 70,
    "product_age_score": 100
  },
  "storage_impact": {
    "temperature_score": 70.0,
    "humidity_score": 40.0,
    "condition_score": 58.0
  },
  "storage_compliance": "needs_attention",
  "recommendations": [
    {
      "priority": "medium",
      "action": "Adjust storage humidity",
      "reason": "Current humidity (37.0%) is suboptimal for paneer (optimal: 40-50%)."
    },
    {
      "priority": "medium",
      "action": "Prioritize stock rotation",
      "reason": "Moderate shelf life remaining (7 days) with moderate risk level."
    }
  ],
  "model_type": "ML_LinearRegression",
  "created_at": "2026-09-25T03:19:26.361121Z"
}
```

- **Verification:**
  - HTTP success: PASS (HTTP 201)
  - Predicted shelf life exists & >= 0: PASS (7 days)
  - Confidence is null: PASS (`null`)
  - Correct model is `paneer_rsl.joblib` (`ML_LinearRegression`): PASS
  - Database record created: PASS (ID 84 in `shelf_life_predictions`)
- **Status: PASS**

---

## 7. Seafood E2E

**Request:** `POST /m3/shelf-life/predict`
```json
{
  "food_type": "seafood",
  "temperature_c": 1.0,
  "humidity_pct": 85.0,
  "storage_duration_days": 1,
  "packaging_type": "open",
  "species": "mackerel"
}
```

**Actual Response:** **HTTP 201 Created**
```json
{
  "id": 87,
  "food_type": "seafood",
  "remaining_shelf_life_days": 2,
  "predicted_expiry_date": "2026-09-27",
  "confidence": null,
  "risk_level": "high",
  "official_freshness_score": 58,
  "score_components": {
    "visual_condition_score": 70,
    "storage_condition_score": 83,
    "shelf_life_score": 40,
    "product_age_score": 100
  },
  "storage_impact": {
    "temperature_score": 100.0,
    "humidity_score": 100.0,
    "condition_score": 83.0
  },
  "storage_compliance": "compliant",
  "recommendations": [
    {
      "priority": "high",
      "action": "Expedite dispatch / immediate sale",
      "reason": "Critical shelf life (2 days) and high spoilage risk."
    },
    {
      "priority": "low",
      "action": "Maintain current storage conditions",
      "reason": "Storage conditions are optimal for seafood."
    }
  ],
  "model_type": "ML_RandomForestRegressor",
  "created_at": "2026-09-25T03:19:26.445544Z"
}
```

- **Species Variations Verified:**
  - `species="mackerel"` → **HTTP 201 Created** (RSL: 2 days)
  - `species="tilapia"` → **HTTP 201 Created** (RSL: 2 days)
  - `species="tuna"` → **HTTP 201 Created** (RSL: 2 days)
- **Verification:**
  - HTTP success: PASS (HTTP 201)
  - RSL >= 0: PASS (2 days)
  - Confidence is null: PASS (`null`)
  - Model = `seafood_rsl.joblib` (`ML_RandomForestRegressor`): PASS
  - Database persistence: PASS (ID 87 in `shelf_life_predictions`)
- **Status: PASS**

---

## 8. Unsupported Categories

Tested with real authenticated `POST /m3/shelf-life/predict` requests:

| Category Tested | Expected Status | Actual Status | Actual Error Message |
|-----------------|-----------------|---------------|----------------------|
| **Chicken** | HTTP 422 | **HTTP 422** | `"ML shelf-life prediction is currently unsupported for this food category."` |
| **Avocado** | HTTP 422 | **HTTP 422** | `"ML shelf-life prediction is currently unsupported for this food category."` |
| **Bakery** | HTTP 422 | **HTTP 422** | `"ML shelf-life prediction is currently unsupported for this food category."` |
| **Packaged Foods** | HTTP 422 | **HTTP 422** | `"ML shelf-life prediction is currently unsupported for this food category."` |
| **Beverages** | HTTP 422 | **HTTP 422** | `"ML shelf-life prediction is currently unsupported for this food category."` |

- **Verification:**
  - No successful prediction: PASS
  - No 7-day fallback: PASS
  - No rule-based fallback: PASS
  - No fabricated confidence: PASS
  - No database records created for rejected requests: PASS (0 rows added)
- **Status: PASS**

---

## 9. Domain Validation

Out-of-domain test inputs executed against `POST /m3/shelf-life/predict`:

| Target Category | Tested Out-of-Domain Parameter | Actual Status | Actual Response Detail |
|---|---|---|---|
| Tomato | `temperature_c = 19.0` (<20°C) | **HTTP 422** | `Storage temperature 19.0°C is outside validated ML domain (20.0–25.0°C) for tomato.` |
| Tomato | `temperature_c = 26.0` (>25°C) | **HTTP 422** | `Storage temperature 26.0°C is outside validated ML domain (20.0–25.0°C) for tomato.` |
| Tomato | `humidity_pct = 64.0` (<65%) | **HTTP 422** | `Relative humidity 64.0% is outside validated ML domain (65.0–75.0%) for tomato.` |
| Tomato | `humidity_pct = 76.0` (>75%) | **HTTP 422** | `Relative humidity 76.0% is outside validated ML domain (65.0–75.0%) for tomato.` |
| Tomato | `storage_duration_days = 36` (>35d) | **HTTP 422** | `Storage duration 36.0 days is outside validated ML domain (0.0–35.0 days) for tomato.` |
| Tomato | `packaging_type = "sealed"` (invalid) | **HTTP 422** | `Packaging type 'sealed' is outside validated ML domain (uncoated, beeswax_coated) for tomato.` |
| Paneer | `temperature_c = 3.0` (<4°C) | **HTTP 422** | `Storage temperature 3.0°C is outside validated ML domain (4.0–8.0°C) for paneer.` |
| Paneer | `temperature_c = 9.0` (>8°C) | **HTTP 422** | `Storage temperature 9.0°C is outside validated ML domain (4.0–8.0°C) for paneer.` |
| Paneer | `humidity_pct = 29.0` (<30%) | **HTTP 422** | `Relative humidity 29.0% is outside validated ML domain (30.0–50.0%) for paneer.` |
| Paneer | `humidity_pct = 51.0` (>50%) | **HTTP 422** | `Relative humidity 51.0% is outside validated ML domain (30.0–50.0%) for paneer.` |
| Paneer | `storage_duration_days = 16` (>15d) | **HTTP 422** | `Storage duration 16.0 days is outside validated ML domain (0.0–15.0 days) for paneer.` |
| Paneer | `packaging_type = "uncoated"` (invalid) | **HTTP 422** | `Packaging type 'uncoated' is outside validated ML domain (sealed) for paneer.` |
| Seafood | `temperature_c = -0.5` (<0°C) | **HTTP 422** | `Storage temperature -0.5°C is outside validated ML domain (0.0–2.0°C) for seafood.` |
| Seafood | `temperature_c = 3.0` (>2°C) | **HTTP 422** | `Storage temperature 3.0°C is outside validated ML domain (0.0–2.0°C) for seafood.` |
| Seafood | `humidity_pct = 79.0` (<80%) | **HTTP 422** | `Relative humidity 79.0% is outside validated ML domain (80.0–90.0%) for seafood.` |
| Seafood | `humidity_pct = 91.0` (>90%) | **HTTP 422** | `Relative humidity 91.0% is outside validated ML domain (80.0–90.0%) for seafood.` |
| Seafood | `storage_duration_days = 4` (>3d) | **HTTP 422** | `Storage duration 4.0 days is outside validated ML domain (0.0–3.0 days) for seafood.` |
| Seafood | `species = "salmon"` (unapproved) | **HTTP 422** | `Species 'salmon' is outside validated ML domain (mackerel, tilapia, tuna) for seafood.` |
| Seafood | `packaging_type = "vacuum_sealed"` | **HTTP 422** | `Packaging type 'vacuum_sealed' is outside validated ML domain (open) for seafood.` |

- **Verification:**
  - No clamping, silent modification, or extrapolation: PASS
  - No orphaned database rows created on out-of-domain failure: PASS
- **Status: PASS**

---

## 10. Database Persistence

Verified via direct SQL query on table `shelf_life_predictions` in PostgreSQL:
```sql
SELECT id, food_type, remaining_shelf_life_days, model_type, confidence, storage_condition_id, risk_level, created_at
FROM shelf_life_predictions
WHERE id IN (81, 84, 87);
```

**Actual SQL Records:**
- **Row 1:** `id=81`, `food_type='tomato'`, `remaining_shelf_life_days=26`, `model_type='ML_RandomForestRegressor'`, `confidence=NULL`, `storage_condition_id=222`, `risk_level='low'`, `created_at=2026-09-25 03:19:26.230876+00`
- **Row 2:** `id=84`, `food_type='paneer'`, `remaining_shelf_life_days=7`, `model_type='ML_LinearRegression'`, `confidence=NULL`, `storage_condition_id=225`, `risk_level='moderate'`, `created_at=2026-09-25 03:19:26.361121+00`
- **Row 3:** `id=87`, `food_type='seafood'`, `remaining_shelf_life_days=2`, `model_type='ML_RandomForestRegressor'`, `confidence=NULL`, `storage_condition_id=228`, `risk_level='high'`, `created_at=2026-09-25 03:19:26.445544+00`

- **Status: PASS**

---

## 11. History

**Request:** `GET /m3/shelf-life/history` with JWT Token
- **Actual HTTP Status:** **HTTP 200 OK**
- **Record Count:** Returned 9 historical records for the test session.
- **Verification:** Newly created prediction IDs (81, 84, 87) are present in the returned list, sorted by `created_at` descending.
- **Status: PASS**

---

## 12. Recommendations

**Request:** `GET /m3/recommendations/81` with JWT Token
- **Actual HTTP Status:** **HTTP 200 OK**
- **Actual Output:**
  ```json
  [
    {
      "priority": "low",
      "action": "Maintain current storage conditions",
      "reason": "Storage conditions are optimal for tomato."
    },
    {
      "priority": "low",
      "action": "Standard FEFO rotation",
      "reason": "Sufficient shelf life remaining (26 days)."
    }
  ]
  ```
- **Status: PASS**

---

## 13. Analytics

**Request:** `GET /m3/analytics` with JWT Token
- **Actual HTTP Status:** **HTTP 200 OK**
- **Actual Output:**
  ```json
  {
    "total_predictions": 9,
    "average_freshness_score": 67.22,
    "average_remaining_shelf_life_days": 13.78,
    "risk_counts": {
      "low": 4,
      "moderate": 1,
      "high": 4
    },
    "freshness_trend": [
      { "date": "2026-09-25", "average_score": 67.22, "count": 9 }
    ]
  }
  ```
- **Verification:** No database/schema errors, transparently computes statistics across actual predictions.
- **Status: PASS**

---

## 14. Expiring Inventory

**Request:** `GET /inventory/expiring-soon?days=7` with JWT Token
- **Actual HTTP Status:** **HTTP 200 OK**
- **Actual Output:** `[]` (0 items expiring in 7 days for new user; schema valid)
- **Status: PASS**

---

## 15. Rotation Suggestions

**Request:** `GET /m3/rotation-suggestions` with JWT Token
- **Actual HTTP Status:** **HTTP 200 OK**
- **Actual Output:**
  ```json
  {
    "total_items": 0,
    "suggestions": []
  }
  ```
- **Verification:** FEFO rotation suggestion logic returns structured response without error.
- **Status: PASS**

---

## 16. M1 Regression

**Command:**
```powershell
& "D:\infosys\project 1\backend\.venv\Scripts\python.exe" test_flow.py
```

**Actual Execution Result:**
- **Modules Executed:** 10
- **Passed:** 10 / 10
- **Failed:** 0
- **Modules Verified:**
  1. Native Bcrypt Password Hashing & Verification: OK
  2. Registration for All 5 Official Roles: OK
  3. Duplicate Email Prevention: OK (HTTP 409)
  4. Invalid Role Prevention: OK (HTTP 400)
  5. Login & Authentication: OK
  6. `/auth/me` User Profile Verification: OK
  7. Inventory Registration across all 8 Official Food Categories: OK
  8. Inventory Listing & Data Retrieval: OK
  9. Dynamic Availability & Expiry Status Logic: OK
  10. Item Deletion: OK
- **Summary:** `ALL 10 VERIFICATION MODULES PASSED WITH 100% SUCCESS!`
- **Status: PASS**

---

## 17. M2 Regression

**Command:**
```powershell
& "D:\infosys\project 1\backend\.venv\Scripts\python.exe" test_m2.py
```

**Actual Execution Result:**
- Image Analysis Module: PASS
- Freshness Assessment Mapping Logic: PASS
- Dataset Utilities & Split Creation: PASS
- FastAPI M2 Endpoints (`/analysis/predict`, `/analysis/history`): PASS
- M1 Regression under M2: PASS
- **Summary:** `ALL M2 VERIFICATION TESTS PASSED [OK]`
- **Status: PASS**

---

## 18. Model Mapping

Verified via code inspection in `app/ml/rsl_predictor.py`, `saved_models/model_registry.json`, and runtime responses:

| Category | Model Artifact | Architecture / Pipeline | Status |
|---|---|---|---|
| **Tomato** | `tomato_rsl.joblib` | `ML_RandomForestRegressor` | Validated in production |
| **Paneer** | `paneer_rsl.joblib` | `ML_LinearRegression` | Validated in production |
| **Seafood** | `seafood_rsl.joblib` | `ML_RandomForestRegressor` | Validated in production |

**Unsupported Categories Confirmation:**
- `Chicken`, `Avocado`, `Bakery`, `Packaged Foods`, `Beverages` are rejected with HTTP 422 before any ML model is invoked.
- `chicken_rsl.joblib` is isolated and blocked in the model registry.
- **Status: PASS**

---

## 19. Security

| Security Check | Expected Behavior | Actual Behavior | Result |
|---|---|---|---|
| Unauthenticated M3 Predict | HTTP 401 | HTTP 401 | PASS |
| Invalid JWT Token | HTTP 401 | HTTP 401 | PASS |
| Unauthenticated History/Analytics | HTTP 401 | HTTP 401 | PASS |
| Register with Unofficial Role | HTTP 400 | HTTP 400 | PASS |
| Login with Invalid Password | HTTP 401 | HTTP 401 | PASS |
| `/auth/me` Password Leaks | No password/hash exposed | Exposes `id`, `email`, `role`, `full_name` only | PASS |
| Direct Model File Access (`/saved_models/*.joblib`) | HTTP 404 Not Found | HTTP 404 for all static/ml paths | PASS |
| OpenAPI Schema `.joblib` Leaks | No `.joblib` references | Checked OpenAPI spec; 0 `.joblib` references | PASS |
| Internal Traceback / Secrets in Error Response | Clean JSON error | HTTP 422 cleanly formatted `{"detail": "..."}` | PASS |

- **Status: PASS**

---

## 20. Local Performance

Measured via 5 real loopback HTTP requests per approved category against `http://127.0.0.1:8000`:

| Category | Min Latency | Max Latency | Mean (Avg) Latency | Median Latency | Samples (ms) |
|---|---|---|---|---|---|
| **Tomato** | 25.51 ms | 29.56 ms | **27.47 ms** | 26.99 ms | [26.99, 26.42, 25.51, 28.85, 29.56] |
| **Paneer** | 18.06 ms | 19.41 ms | **18.72 ms** | 18.61 ms | [18.61, 18.18, 18.06, 19.41, 19.36] |
| **Seafood** | 23.79 ms | 25.57 ms | **24.41 ms** | 24.29 ms | [23.85, 24.56, 23.79, 25.57, 24.29] |

*Note: Latencies represent local loopback measurements on Windows 11 host. Not intended as cloud/production SLA claims.*

- **Status: PASS**

---

## 21. Browser/API Validation

**Browser-level network validation was not available in this environment.**

- **Rationale:** Standard browser CDP automation against headless Chrome instances in this environment encountered local websocket transport constraints.
- **Alternative Verification:** Comprehensive end-to-end HTTP validation was executed using the full API layer against the live running FastAPI server and PostgreSQL database (70 checks, 70 passed).
- **Status: PASS WITH LIMITATIONS**

---

## 22. Issues Found

1. **Unsupported seafood species field handling in test harness**: In `schemas.py`, the schema field is `species`, while older test scripts passed `seafood_species`. Resolved in the test caller by passing the standard schema parameter `species`.
2. **Missing pandas dependency in `.venv` (Prior step)**: Previously resolved with `pip install pandas` in the virtual environment.

---

## 23. Fixes Made

- No application code, ML models, or database schemas required modification during this run. All application endpoints, domain checks, model registry mappings, and security boundaries functioned as designed.

---

## 24. Limitations

- **Browser-level automation**: Validated extensively through authenticated HTTP API requests, database queries, and static frontend build verification rather than end-to-end browser drivers.

---

## 25. Final Status

### **PASS WITH LIMITATIONS**
*(Substantive API, ML model, database, and integration validations passed 100%; browser-level network validation was not available in this environment).*
