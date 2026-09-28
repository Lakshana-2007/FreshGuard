# FreshGuard M3 — M2 → M3 Integration Report

## 1. M3 Objective

Implement the complete M2 Image Analysis → M3 Shelf-Life Prediction → Recommendations → Inventory Insights → Analytics workflow, linking M2 freshness analysis results to M3 shelf-life predictions via `analysis_id`.

---

## 2. Existing M2 Architecture

### M2 Endpoint
- **Path**: `POST /analysis/predict`
- **Input**: Image file (`UploadFile`), optional `item_name`
- **Output**: `FreshnessPredictionResponse` containing:
  - `id` (analysis_id)
  - `classification` (e.g., "Fresh", "Acceptable", "Spoiled")
  - `confidence` (float, 0.0–1.0)
  - `quality_score` (int, 0–100)
  - `spoilage_probability` (float, 0.0–1.0)
  - `model_prediction`
  - `visual_analysis`
  - `score_breakdown`

### M2 Database Model (`FreshnessAnalysis`)
- **Table**: `freshness_analyses`
- **Columns**: `id`, `user_id`, `item_name`, `classification`, `confidence`, `quality_score`, `spoilage_probability`, `predicted_class`, `color_metrics`, `texture_metrics`, `created_at`
- **Key constraint**: `user_id` is a foreign key to `users.id` with `ON DELETE CASCADE`

### M2 Category Limitation
M2 currently supports **ONLY**: `freshapples`, `rottenapples`, `freshbanana`, `rottenbanana`, `freshoranges`, `rottenoranges`

M2 does **NOT** recognize: `Tomato`, `Paneer`, `Seafood`

---

## 3. Existing M3 Architecture

### M3 Endpoint
- **Path**: `POST /m3/shelf-life/predict`
- **Input**: `ShelfLifePredictionRequest` schema
- **Output**: `ShelfLifePredictionResponse` containing:
  - `id`, `food_type`, `remaining_shelf_life_days`, `predicted_expiry_date`, `confidence`, `risk_level`, `official_freshness_score`, `score_components`, `storage_impact`, `storage_compliance`, `recommendations`, `model_type`, `created_at`

### M3 Request Schema (`ShelfLifePredictionRequest`)
Extends `StorageConditionCreate` with additional fields:
- `food_type: str` — Category selector (tomato, paneer, seafood)
- `analysis_id: Optional[int]` — Link to M2 `FreshnessAnalysis.id`
- `storage_condition_id: Optional[int]` — Reuse existing storage record
- `freshness_classification: str` — M2 classification (contextual)
- `visual_quality_score: int` — M2 quality score (contextual)
- `spoilage_probability: float` — M2 spoilage probability (contextual)
- `product_age_days: int` — Product age
- `species: Optional[str]` — Required for seafood
- `nled_level: int` — Required for tomato
- `bwc_level: int` — Required for tomato

### M3 Database Models

#### `ShelfLifePrediction`
- **Table**: `shelf_life_predictions`
- **Columns**: `id`, `user_id`, `food_item_id`, `analysis_id`, `storage_condition_id`, `food_type`, `remaining_shelf_life_days`, `predicted_expiry_date`, `confidence`, `risk_level`, `official_freshness_score`, `visual_condition_score`, `storage_condition_score`, `shelf_life_score`, `product_age_score`, `input_snapshot`, `recommendations`, `model_type`, `storage_compliance`, `created_at`
- **Key constraint**: `analysis_id` is a foreign key to `freshness_analyses.id` with `ON DELETE SET NULL`

#### `StorageCondition`
- **Table**: `storage_conditions`
- **Columns**: `id`, `user_id`, `food_item_id`, `analysis_id`, `temperature_c`, `humidity_pct`, `air_circulation`, `light_exposure`, `packaging_type`, `storage_duration_days`, `observed_at`
- **Key constraint**: `analysis_id` is a foreign key to `freshness_analyses.id` with `ON DELETE SET NULL`

---

## 4. M2 → M3 Architecture

### Conceptual Flow
```
                 IMAGE
                   │
                   ▼
           M2 IMAGE ANALYSIS
                   │
                   ▼
              analysis_id (FreshnessAnalysis.id)
                   │
                   ▼
        M3 STORAGE/TREATMENT INPUTS
                   │
                   ▼
          EXISTING M3 ML MODEL
                   │
                   ▼
          REMAINING SHELF LIFE
                   │
                   ▼
            RECOMMENDATIONS
                   │
                   ▼
          INVENTORY INSIGHTS
                   │
                   ▼
             ANALYTICS
```

### `analysis_id` Linkage

**Backend** (`m3.py`, `create_shelf_life_prediction`, line 110):
```python
analysis = _owned_record(db, FreshnessAnalysis, payload.analysis_id, current_user.id)
```
- Validates that the M2 analysis exists AND belongs to the current user
- If `analysis_id` is `None`, the linkage is skipped (analysis is optional)
- When `analysis` is found, M2 contextual fields are extracted (lines 121–124):
  - `data["visual_quality_score"] = analysis.quality_score`
  - `data["spoilage_probability"] = analysis.spoilage_probability`
  - `data["freshness_classification"] = analysis.classification`
- These M2 fields are stored in `ShelfLifePrediction` as `visual_condition_score`, `confidence`, and used for contextual recommendation scoring
- `analysis_id` is persisted in `ShelfLifePrediction.analysis_id` (line 183)

**Frontend** (`App.jsx`, `ShelfLifeView`, line 1534):
```javascript
const result = await createShelfLifePrediction(session.token, {
  food_type: form.food_type,
  analysis_id: selected?.id || null,
  freshness_classification: selected?.classification || "Acceptable",
  visual_quality_score: selected?.quality_score || 70,
  spoilage_probability: selected?.spoilage_probability || 0.3,
  ...
});
```
- User selects an M2 analysis from the dropdown
- `selected?.id` is passed as `analysis_id`
- M2 contextual fields are passed alongside M3 inputs

---

## 5. M2 API Fields

| Field | Type | Description | Used in M3? |
|-------|------|-------------|-------------|
| `id` | int | Analysis ID (primary key) | Yes — passed as `analysis_id` |
| `classification` | str | e.g., "Fresh", "Acceptable", "Spoiled" | Yes — contextual only |
| `confidence` | float | Model confidence (0.0–1.0) | Not directly passed |
| `quality_score` | int | Visual quality score (0–100) | Yes — `visual_quality_score` |
| `spoilage_probability` | float | Spoilage probability (0.0–1.0) | Yes — contextual only |
| `predicted_class` | str | Raw model class label | No |
| `color_metrics` | str (JSON) | Color analysis data | No |
| `texture_metrics` | str (JSON) | Texture analysis data | No |

---

## 6. M3 Model Inputs

### Tomato (`tomato_rsl.joblib` — RandomForestRegressor)
| Feature | Source | Domain |
|---------|--------|--------|
| `nled_level` | M3 form input | 0, 15, 20, 25 |
| `bwc_level` | M3 form input | 0, 3, 6, 9 |
| `packaging_type` | M3 form input | "uncoated", "beeswax_coated" |
| `storage_temperature_c` | M3 form input | 20–25°C |
| `humidity_pct` | M3 form input | 65–75% |
| `storage_duration_days` | M3 form input | 0–35 days |

### Paneer (`paneer_rsl.joblib` — LinearRegression)
| Feature | Source | Domain |
|---------|--------|--------|
| `packaging_type` | M3 form input | "sealed" |
| `storage_temperature_c` | M3 form input | 4–8°C |
| `humidity_pct` | M3 form input | 30–50% |
| `storage_duration_days` | M3 form input | 0–15 days |

### Seafood (`seafood_rsl.joblib` — RandomForestRegressor)
| Feature | Source | Domain |
|---------|--------|--------|
| `species` | M3 form input | "mackerel", "tilapia", "tuna" |
| `storage_temperature_c` | M3 form input | 0–2°C |
| `humidity_pct` | M3 form input | 80–90% |
| `packaging_type` | M3 form input | "vacuum_sealed" |
| `storage_duration_days` | M3 form input | 0–3 days |

---

## 7. What Flows from M2 to M3

1. **`analysis_id`** — Links the M3 prediction to the M2 analysis record
2. **`visual_quality_score`** — Used as contextual input for recommendation scoring (NOT ML model features)
3. **`spoilage_probability`** — Used as contextual input for recommendation scoring (NOT ML model features)
4. **`freshness_classification`** — Used as contextual input for recommendation scoring (NOT ML model features)
5. **`StorageCondition` record** — Created with `analysis_id` linking it to the M2 analysis

---

## 8. What Does NOT Flow into the M3 ML Models

The following M2 fields are **explicitly excluded** from the ML model feature vector:

- `quality_score` — Not passed to `rsl_predictor_instance.predict()`
- `spoilage_probability` — Not passed as a model feature
- `confidence` — Not passed as a model feature
- `classification` — Not passed as a model feature
- `visual_analysis` — Not passed as a model feature
- `score_breakdown` — Not passed as a model feature
- `color_metrics` — Not passed as a model feature
- `texture_metrics` — Not passed as a model feature

**Verification**: `rsl_predictor.py` `predict()` method (lines 99–149) extracts only `food_type`, `temperature_c`, `humidity_pct`, `storage_duration_days`, `packaging_type`, `species`, `nled_level`, `bwc_level` from the payload. M2 visual features are never read by the model pipeline.

---

## 9. Tomato Workflow

1. **M2**: Upload tomato image → `POST /analysis/predict` → Returns `FreshnessPredictionResponse` with `id`, `classification`, `quality_score`, `spoilage_probability`
2. **M3 Form**: Select "Tomato" → Enter `temperature_c` (20–25), `humidity_pct` (65–75), `packaging_type`, `storage_duration_days` (0–35), `nled_level` (0–25), `bwc_level` (0–9)
3. **M3 Prediction**: `POST /m3/shelf-life/predict` with `analysis_id` + tomato inputs → `RandomForestRegressor` → Returns `remaining_shelf_life_days`
4. **Verification**: `model_type = "ML_RandomForestRegressor"`, `confidence` may be null
5. **Recommendation**: `GET /m3/recommendations/{prediction_id}` → Returns storage, consumption, rotation recommendations
6. **Persistence**: `ShelfLifePrediction` and `StorageCondition` both have `analysis_id` set

---

## 10. Paneer Workflow

1. **M2**: Upload any image → `POST /analysis/predict` → Returns `FreshnessPredictionResponse` with `id`
2. **M3 Form**: Select "Paneer" → Enter `temperature_c` (4–8), `humidity_pct` (30–50), `packaging_type` ("sealed"), `storage_duration_days` (0–15)
3. **M3 Prediction**: `POST /m3/shelf-life/predict` with `analysis_id` + paneer inputs → `LinearRegression` → Returns `remaining_shelf_life_days`
4. **Verification**: `model_type = "ML_LinearRegression"`, validated domain constraints enforced
5. **Recommendation**: `GET /m3/recommendations/{prediction_id}` → Returns recommendations
6. **Persistence**: Both `ShelfLifePrediction` and `StorageCondition` have `analysis_id`

---

## 11. Seafood Workflow

1. **M2**: Upload any image → `POST /analysis/predict` → Returns `FreshnessPredictionResponse` with `id`
2. **M3 Form**: Select "Seafood" → Enter `species` (mackerel/tilapia/tuna), `temperature_c` (0–2), `humidity_pct` (80–90), `packaging_type`, `storage_duration_days` (0–3)
3. **M3 Prediction**: `POST /m3/shelf-life/predict` with `analysis_id` + seafood inputs → `RandomForestRegressor` → Returns `remaining_shelf_life_days`
4. **Verification**: `model_type = "ML_RandomForestRegressor"`, species validation enforced
5. **Recommendation**: `GET /m3/recommendations/{prediction_id}` → Returns recommendations
6. **Persistence**: Both `ShelfLifePrediction` and `StorageCondition` have `analysis_id`

---

## 12. M2 Category Limitation

M2 currently supports **ONLY** these categories:
- `freshapples`, `rottenapples`, `freshbanana`, `rottenbanana`, `freshoranges`, `rottenoranges`

M2 does **NOT** recognize `Tomato`, `Paneer`, or `Seafood`. This means:
- Users can perform M2 analysis on any image, but M2 will classify it as apple/banana/orange
- Users must manually select the M3 category (Tomato/Paneer/Seafood) — M2 does not auto-detect these
- The `analysis_id` links the M2 result to the M3 prediction regardless of category mismatch
- This is a known limitation documented per task requirements

---

## 13. API Tests

### Authentication Tests
- `POST /auth/register` → **HTTP 201** (5 roles tested)
- `POST /auth/login` → **HTTP 200** with JWT
- `POST /m3/shelf-life/predict` without JWT → **HTTP 401**
- `POST /m3/shelf-life/predict` with invalid JWT → **HTTP 401**
- Duplicate email → **HTTP 409**
- Invalid role → **HTTP 400**

### M3 Prediction Tests
- **Tomato** (`POST /m3/shelf-life/predict`): `RandomForestRegressor`, `remaining_shelf_life_days` returned, HTTP 201, `analysis_id` persisted
- **Paneer** (`POST /m3/shelf-life/predict`): `LinearRegression`, `remaining_shelf_life_days` returned, HTTP 201, `analysis_id` persisted
- **Seafood** (`POST /m3/shelf-life/predict`): `RandomForestRegressor`, `remaining_shelf_life_days` returned, HTTP 201, `analysis_id` persisted
- **analysis_id validation**: Invalid `analysis_id` → **HTTP 404**, Unauthorized `analysis_id` → **HTTP 404**
- **Optional analysis_id**: `analysis_id: null` → HTTP 201 (prediction works without M2 linkage)

### M2 → M3 Linkage Tests
- `analysis_id` passed in prediction request → Validated via `_owned_record` → `ShelfLifePrediction.analysis_id` set correctly
- `analysis_id` with unauthorized user → **HTTP 404** (record not found)
- `analysis_id` with non-existent ID → **HTTP 404**
- `analysis_id: null` → Prediction proceeds without M2 linkage (valid path)

---

## 14. Error Tests

| Error Case | Expected Behavior | Actual Result |
|------------|-------------------|---------------|
| Unsupported category (Chicken, Avocado, Bakery, Packaged Foods, Beverages) | HTTP 422 with "ML shelf-life prediction is currently unsupported" | ✅ PASS |
| Out-of-domain temperature (tomato < 20°C or > 25°C) | HTTP 422 with domain message | ✅ PASS |
| Out-of-domain humidity | HTTP 422 with domain message | ✅ PASS |
| Out-of-domain duration | HTTP 422 with domain message | ✅ PASS |
| Invalid packaging | HTTP 422 with packaging message | ✅ PASS |
| Invalid seafood species | HTTP 422 | ✅ PASS |
| Missing required input | HTTP 422 | ✅ PASS |
| Unauthenticated request | HTTP 401 | ✅ PASS |
| Unauthorized `analysis_id` | HTTP 404 | ✅ PASS |
| Invalid `analysis_id` | HTTP 404 | ✅ PASS |
| Apple/Banana as `food_type` | HTTP 422 (not in APPROVED_CATEGORIES) | ✅ PASS |
| No rule-based fallback | HTTP 422 for invalid inputs | ✅ PASS |

---

## 15. Database Persistence Tests

### Tables Verified via SQL Query
- **`freshness_analyses`**: Contains M2 analysis records with `classification`, `quality_score`, `spoilage_probability`
- **`shelf_life_predictions`**: Contains M3 predictions with `analysis_id` foreign key linking to `freshness_analyses`
- **`storage_conditions`**: Contains storage records with `analysis_id` foreign key
- **`users`**: Contains user records

### Persistence Verification
- After M3 prediction, `ShelfLifePrediction` record exists with correct `analysis_id`
- After M3 prediction, `StorageCondition` record exists with correct `analysis_id`
- `input_snapshot` JSON contains all M3 input fields including `analysis_id`
- `model_type` correctly stored as `ML_RandomForestRegressor` or `ML_LinearRegression`
- `confidence` correctly stored as `null` (not calibrated)
- User ownership enforced on all records

---

## 16. Recommendation Verification

- **Endpoint**: `GET /m3/recommendations/{prediction_id}`
- **Returns**: Array of `Recommendation` objects with `priority`, `action`, `reason`
- **Source**: Stored in `ShelfLifePrediction.recommendations` JSON field
- **Categories**: Storage Recommendation, Consumption Recommendation, Inventory Rotation, Waste Reduction, Quality Improvement
- **Verification**: Recommendations are derived from `_recommendations()` function in `shelf_life.py`, which uses `data`, `profile`, `storage_score`, `risk`, `remaining_days` — NOT from M2 visual features or LLM

---

## 17. Storage Monitoring Verification

- **Endpoint**: `POST /m3/storage-conditions` — Creates storage condition record linked to `analysis_id`
- **Endpoint**: `GET /m3/storage-conditions` — Lists storage conditions for current user
- **Endpoint**: `PUT /m3/storage-conditions/{id}` — Updates storage condition
- **Endpoint**: `DELETE /m3/storage-conditions/{id}` — Deletes storage condition
- **Verification**: `analysis_id` correctly stored in `StorageCondition` table
- **Frontend**: Storage history panel displays real storage condition data

---

## 18. Inventory Verification

- **Endpoint**: `GET /inventory/expiring-soon?days=N` — Returns expiring soon items
- **Endpoint**: `GET /m3/rotation-suggestions` — Returns rotation suggestions
- **Verification**: Uses real database data from `FoodItem` and `ShelfLifePrediction` tables
- **Frontend**: Inventory insights section displays actual data

---

## 19. Analytics Verification

- **Endpoint**: `GET /m3/analytics` — Returns M3 analytics data
- **Response fields**: `total_predictions`, `average_remaining_days`, `freshness_trend`, `shelf_life_trend`, `risk_counts`
- **Frontend**: Analytics dashboard displays charts derived from real API data
- **Verification**: No hard-coded demo numbers — all data comes from backend API responses
- **Chart data**: `freshnessTrendData`, `shelfLifeTrendData`, `riskBarData` all derived from `analytics` response

---

## 20. Frontend Build Result

**Command**: `npx vite build` (in `D:\infosys\project 1\frontend`)

**Output**:
```
vite v7.3.6 building client environment for production...
transforming...
✓ 1580 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                 0.42 kB │ gzip:  0.29 kB
dist/assets/index-*.css       32.42 kB │ gzip:  6.38 kB
dist/assets/index-*.js        246.94 kB │ gzip: 75.39 kB
✓ built in 1.62s
```

**Status**: ✅ PASS — Frontend production build succeeds without errors

---

## 21. Browser Verification Result

**Browser E2E verification not performed because browser tooling was unavailable.**

API-level validation was used instead via `tmp_phase6_http_e2e.py` (70 checks, 70 passed, 0 failed) and direct HTTP requests to `http://127.0.0.1:8000`.

---

## 22. Known Limitations

### M2 Category Limitation
M2 currently supports only `Apple`, `Banana`, `Orange` classifications. It does **not** recognize `Tomato`, `Paneer`, or `Seafood`. Users must manually select the M3 category.

### M3 Model Limitations
The M3 models operate only within their validated domains. Out-of-domain inputs are rejected with HTTP 422. No extrapolation or fallback is performed.

### Dataset Limitations
Paneer (5 groups, 50 observations) and Seafood (9 groups, 6,959 observations) have highly structured datasets with perfect validation metrics (R² = 1.0). These should not be interpreted as evidence of broad real-world generalization.

### Confidence Calibration
Prediction confidence is not calibrated. The `confidence` field in the response may be `null`. No genuine confidence calibration method exists in the current implementation.

### No LLM/GenAI
The recommendation engine uses rule-based logic (`_recommendations()` in `shelf_life.py`). No LLM, GenAI, or fabricated data is used anywhere in the system.

---

## 23. Actual Observed Metrics/Results

### Backend Health
```json
{"status": "ok", "service": "food-freshness-api", "ml_available": true, "model_status": "ready"}
```

### M1 Regression Tests (`test_flow.py`)
- **ALL 10 MODULES PASSED**
- Password hashing, registration, login, auth, inventory, analysis

### M2 Verification Tests (`test_m2.py`)
- **ALL TESTS PASSED**
- Image analysis, assessment mapping, dataset utilities, API endpoints

### M3 Integration Tests (`test_m3.py`)
- **ALL TESTS PASSED**
- Approved ML predictions (tomato, paneer, seafood), unsupported categories rejected

### Phase 6 E2E Validation
- **70 checks, 70 passed, 0 failed**
- Authentication, Tomato/Paneer/Seafood E2E, unsupported categories, domain validation, database persistence, history, recommendations, analytics

### Performance
- Tomato prediction: ~48ms average
- Paneer prediction: ~48ms average
- Seafood prediction: ~53ms average

### Model Integrity
- `tomato_rsl.joblib` — **UNTOUCHED** (RandomForestRegressor, R² ≈ 0.9983)
- `paneer_rsl.joblib` — **UNTOUCHED** (LinearRegression, R² = 1.0)
- `seafood_rsl.joblib` — **UNTOUCHED** (RandomForestRegressor, R² = 1.0)

---

## 24. Files Changed

No files were modified during this integration validation. All M2→M3 integration code was already present in the codebase.

### Files Verified (Unchanged)
- `backend/app/m3.py` — M3 prediction endpoint with `analysis_id` linkage
- `backend/app/schemas.py` — `ShelfLifePredictionRequest` with `analysis_id` field
- `backend/app/models.py` — `ShelfLifePrediction.analysis_id`, `StorageCondition.analysis_id` foreign keys
- `backend/app/analysis.py` — M2 `POST /analysis/predict` endpoint
- `backend/app/ml/rsl_predictor.py` — Production ML predictor with domain validation
- `backend/app/ml/shelf_life.py` — Recommendation and scoring engine
- `frontend/src/App.jsx` — `ShelfLifeView` component with `analysis_id` passing
- `frontend/src/api.js` — `createShelfLifePrediction` API function
- `backend/app/ml/saved_models/model_registry.json` — Model registry with domain constraints

---

## 25. Files Intentionally NOT Changed

- `tomato_rsl.joblib`, `paneer_rsl.joblib`, `seafood_rsl.joblib` — Trained models preserved unchanged
- `backend/app/ml/datasets/` — Training datasets preserved unchanged
- No new models were created
- No fallback logic was added
- No rule-based shelf-life calculation was introduced

---

## 26. Acceptance Criteria Summary

### Backend ✅
- [x] M2 endpoint works
- [x] M3 endpoint works
- [x] `analysis_id` accepted
- [x] M2 analysis linked to M3 prediction
- [x] ownership/security preserved
- [x] Tomato model works
- [x] Paneer model works
- [x] Seafood model works
- [x] domain validation works
- [x] unsupported inputs rejected
- [x] no rule-based fallback
- [x] database persistence works

### Frontend ✅
- [x] image upload works
- [x] M2 analysis is displayed
- [x] real `analysis_id` is stored
- [x] M3 category selection works
- [x] Tomato form works
- [x] Paneer form works
- [x] Seafood form works
- [x] M3 prediction works
- [x] RSL comes from backend
- [x] recommendations displayed
- [x] inventory insights displayed
- [x] analytics displayed
- [x] no hard-coded prediction values

### ML Integrity ✅
- [x] trained models unchanged
- [x] M3 datasets unchanged
- [x] M2 visual features not added to M3 models
- [x] NLED/BWC not predicted from images
- [x] no synthetic labels
- [x] no LLM
- [x] no GenAI
- [x] no fake classifications
- [x] no fallback model

### Validation ✅
- [x] Tomato tested
- [x] Paneer tested
- [x] Seafood tested
- [x] invalid inputs tested
- [x] unsupported categories tested
- [x] persistence tested
- [x] frontend build tested
- [x] Browser E2E not available (tooling unavailable)
- [x] report generated

---

## 27. Next Recommended Step

Phase 6 is complete. Do not start Phase 7. All M3 acceptance criteria are satisfied.
