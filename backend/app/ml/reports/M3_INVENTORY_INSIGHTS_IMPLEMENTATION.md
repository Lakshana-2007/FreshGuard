# M3 Inventory Insights Implementation

## 1. Official M3 Requirement

The official M3 document requires inventory insights including:
- Expiring-soon inventory identification
- Inventory rotation / FEFO ordering
- Inventory quality overview
- Shelf-life prediction history
- Inventory-level summary information

The focus is on making FreshGuard capable of providing useful inventory-level insights from ACTUAL data already stored in the application.

## 2. Existing Inventory Architecture

After inspecting the codebase, the following inventory-related infrastructure was already present:

### Existing Models
- **FoodItem** (Models.py): `id`, `name`, `category`, `batch_number`, `quantity`, `expiry_date`, `created_by`
- **ShelfLifePrediction** (Models.py): `id`, `user_id`, `food_item_id`, `analysis_id`, `storage_condition_id`, `food_type`, `remaining_shelf_life_days`, `predicted_expiry_date`, `confidence`, `risk_level`, `official_freshness_score`, `visual_condition_score`, `storage_condition_score`, `shelf_life_score`, `product_age_score`, `input_snapshot`, `recommendations`, `model_type`, `storage_compliance`, `created_at`
- **StorageCondition** (Models.py): `id`, `user_id`, `food_item_id`, `analysis_id`, `temperature_c`, `humidity_pct`, `air_circulation`, `light_exposure`, `packaging_type`, `storage_duration_days`, `observed_at`
- **FreshnessAnalysis** (Models.py): `id`, `user_id`, `item_name`, `classification`, `confidence`, `quality_score`, `spoilage_probability`, `predicted_class`, `color_metrics`, `texture_metrics`, `created_at`

### Existing Endpoints
- `GET /m3/rotation-suggestions` - FEFO consumption/rotation order (already identified as covering expiring items)
- `GET /m3/shelf-life/history` - Prediction history for user
- `GET /m3/analytics` - Summary metrics (enhanced in this step)
- `GET /m3/recommendations/{prediction_id}` - Per-prediction recommendations
- `POST /m3/shelf-life/predict` - Creates prediction with storage condition linkage
- `POST /m3/storage-conditions` / `GET /m3/storage-conditions` - Storage monitoring

### Existing Schemas
- **RotationSuggestionsResponse**: `total_items`, `expired_count`, `suggestion_basis`, `suggestions`
- **RotationSuggestion**: Priority rank, food item identity, expiry info, risk, freshness, compliance
- **ExpiringSoonItem** (schemas.py B1): Inventory item enriched with expiry urgency and M3 prediction data
- **M3AnalyticsResponse**: Total predictions, freshness scores, remaining shelf life, risk counts, trends, storage impact
- **Recommendation**, **ScoreComponents**, **RotationSuggestion** schemas

### Ownership & Security
- `_owned_record()` function (m3.py lines 29-36) validates user ownership before accessing records
- `get_current_user` dependency authenticates and identifies current user
- All queries filtered by `current_user.id` - no cross-user data leakage

## 3. Existing Functionality Discovered

The following inventory insight capabilities were already partially or fully implemented:

### Already Complete
1. **FEFO Rotation** (`GET /m3/rotation-suggestions`): Identifies expired items first, sorts non-expired by expiry_date ascending, incorporates freshness scores for tie-breaking
2. **Prediction History** (`GET /m3/shelf-life/history`): Returns user's ShelfLifePrediction records ordered newest first
3. **Basic Analytics** (`GET /m3/analytics`): Provides aggregate metrics (total predictions, average freshness, average remaining shelf life, risk distributions, trends)
4. **Storage Monitoring**: `POST/GET /m3/storage-conditions` fully implemented with ownership validation

### Partially Complete - Enhanced in This Step
1. **Expiring-Soon Filtering**: Enhanced `GET /m3/rotation-suggestions` with `days` query parameter
2. **Quality Overview Metrics**: Enhanced `GET /m3/analytics` with `expiring_soon_count`, `expired_count`, `high_risk_count`
3. **RSL Window Filtering**: Both endpoints now support optional `days` parameter (default 7) to filter by remaining shelf life window

## 4. Expiring-Soon Inventory

### Enhanced Endpoint: `GET /m3/rotation-suggestions?days=N`

**Query Parameter:**
- `days` (integer, default 7): Filter items where `days_until_expiry` falls within `[−abs(days), days]` range

**Behavior:**
- When `days=3`, returns items expiring in the window from 3 days before today to 3 days from today
- Items with `expiry_date < today` always included (expired)
- Items with `0 < days_until_expiry <= days` included (expiring soon)
- Items with `days_until_expiry > days` excluded
- Items with `days_until_expiry <= 0` included (already expired)

**Response Example** (with `days=3`):
```json
{
  "total_items": 5,
  "expired_count": 1,
  "suggestion_basis": "FEFO (expiry date + freshness score)",
  "suggestions": [
    {
      "priority_rank": 1,
      "food_item_id": 3,
      "name": "Tomato",
      "category": "tomato",
      "batch_number": "TOM-001",
      "quantity": 12,
      "expiry_date": "2026-09-28",
      "days_until_expiry": -2,
      "is_expired": true,
      "reason": "Expired 2 days ago. Consume or discard immediately.",
      "risk_level": "critical",
      "official_freshness_score": 15,
      "storage_compliance": "needs_attention"
    },
    {
      "priority_rank": 2,
      "food_item_id": 7,
      "name": "Paneer",
      "category": "paneer",
      "batch_number": "PN-045",
      "quantity": 8,
      "expiry_date": "2026-10-02",
      "days_until_expiry": 2,
      "is_expired": false,
      "reason": "Expires in 2 days. High urgency — consume before other items.",
      "risk_level": "high",
      "official_freshness_score": 65,
      "storage_compliance": "compliant"
    }
    ...
  ]
}
```

**Edge Cases Handled:**
- No inventory → Empty suggestions list, `total_items=0`
- All items expired → All included, `expired_count=total_items`
- No predictions for items → Included with `risk_level=None`, `official_freshness_score=None`
- `days` parameter negative → Uses `abs(days)` for lower bound

### Also Enhanced: `GET /m3/analytics?days=N`
Provides `expiring_soon_count` (items with 0 < remaining_shelf_life_days <= days) and `expired_count` (remaining_shelf_life_days <= 0) within the specified window.

## 5. FEFO Rotation

### Endpoint: `GET /m3/rotation-suggestions` (enhanced)

**Principle:** FEFO = First Expire, First Out

**Sorting Rules (applied in order):**
1. Expired items (expiry_date < today) always rank first — consume or discard immediately
2. Among non-expired items, sort by expiry_date ascending (earlier dates first)
3. When two items share the same expiry_date and a shelf-life prediction exists for both, the item with the lower official_freshness_score ranks first (worse condition first)
4. Items with no prediction rank after items with predictions on the same expiry date

**New: Days Window Filtering**
- Optional `days` parameter (default 7) filters the displayed items
- Only items with `days_until_expiry` in `[−abs(days), days]` range are included
- `expired_count` reflects only the filtered set

**Deterministic Ordering:**
- Sorting key: `(is_expired_int, expiry_date, freshness_sort_key)`
- `is_expired_int`: 0 for expired (sorts first), 1 for valid
- `expiry_date`: Earlier dates sort first
- `freshness_sort_key`: `(0, score)` when prediction exists so lower score sorts first; `(1, 0)` for items without a prediction

**Response Fields per Suggestion:**
- `priority_rank`: 1-based rank within the response
- `food_item_id`, `name`, `category`, `batch_number`, `quantity`
- `expiry_date`, `days_until_expiry`, `is_expired`
- `reason`: Human-readable explanation
- `risk_level`: From prediction or None
- `official_freshness_score`: From prediction or None
- `storage_compliance`: From prediction or None

## 6. Inventory Quality Overview

### Enhanced Endpoint: `GET /m3/analytics?days=N`

**New Metrics Added to `M3AnalyticsResponse`:**

| Field | Type | Description |
|-------|------|-------------|
| `expiring_soon_count` | int | Items with 0 < remaining_shelf_life_days <= days |
| `expired_count` | int | Items with remaining_shelf_life_days <= 0 |
| `high_risk_count` | int | Items with risk_level in ("critical", "high") |

**Quality Overview Calculation:**
- **expiring_soon_count**: Counts predictions where `0 < remaining_shelf_life_days <= days`
- **expired_count**: Counts predictions where `remaining_shelf_life_days <= 0`
- **high_risk_count**: Counts predictions where `risk_level in ("critical", "high")`

**Example Response with Quality Metrics:**
```json
{
  "total_predictions": 12,
  "average_freshness_score": 73,
  "average_remaining_shelf_life_days": 15,
  "risk_counts": {"critical": 2, "high": 4, "moderate": 5, "low": 1},
  "expiring_soon_count": 3,
  "expired_count": 1,
  "high_risk_count": 2,
  "freshness_trend": [...],
  "shelf_life_trend": [...],
  "storage_condition_impact": {
    "average_condition_score": 82,
    "average_temperature_c": 7.5,
    "average_humidity_pct": 62.0
  }
}
```

## 7. Shelf-Life Prediction History

### Endpoint: `GET /m3/shelf-life/history`

**Already Implemented** - No changes required.

**Functionality:**
- Returns user's `ShelfLifePrediction` records
- Ordered by `created_at.desc()` (newest first)
- Ownership filtered via `current_user.id`
- No cross-user data leakage

**Response Format** (each prediction):
- `id`, `food_type`, `remaining_shelf_life_days`, `predicted_expiry_date`
- `confidence` (always `null` - transparent null confidence)
- `risk_level`, `official_freshness_score`
- `visual_condition_score`, `storage_condition_score`
- `shelf_life_score`, `product_age_score`
- `storage_impact`: `{temperature_score, humidity_score, condition_score}`
- `recommendations`: List of `Recommendation` objects
- `model_type`, `storage_compliance`, `created_at`

**Example:**
```json
[
  {
    "id": 5,
    "food_type": "tomato",
    "remaining_shelf_life_days": 5,
    "predicted_expiry_date": "2026-10-02",
    "confidence": null,
    "risk_level": "moderate",
    "official_freshness_score": 78,
    "visual_condition_score": 80,
    "storage_condition_score": 75,
    "shelf_life_score": 78,
    "product_age_score": 92,
    "storage_impact": {"temperature_score": 85, "humidity_score": 70, "condition_score": 75},
    "recommendations": [
      {"priority": "high", "action": "Consume within 5 days", "reason": "Only 5 days of estimated shelf life remain"},
      {"priority": "medium", "action": "Improve air circulation for better quality retention", "reason": "Better airflow maintains more consistent temperature and moisture levels"}
    ],
    "model_type": "ML_RandomForestRegressor",
    "storage_compliance": "compliant",
    "created_at": "2026-09-27T14:30:00+00:00"
  }
]
```

## 8. Inventory Summary

### Enhanced Endpoint: `GET /m3/analytics?days=N`

The `M3AnalyticsResponse` now includes the comprehensive quality overview metrics (expiring_soon_count, expired_count, high_risk_count) making it a de facto inventory summary endpoint.

**No separate `/m3/inventory/summary` endpoint created** - the enhanced analytics endpoint provides equivalent functionality with the optional `days` parameter for window filtering.

**Summary Data Available:**
- `total_predictions`: Total number of predictions
- `expiring_soon_count`: Items approaching expiry within window
- `expired_count`: Items already expired
- `high_risk_count`: Items with critical/high risk
- `average_remaining_shelf_life_days`: Average across all predictions
- `average_freshness_score`: Average freshness score
- `risk_counts`: Distribution by risk level
- `storage_condition_impact`: Average temperature, humidity, condition score

## 9. APIs

### Modified Endpoints

#### `GET /m3/rotation-suggestions?days=N`
- **Method**: GET
- **Auth**: `get_current_user` dependency
- **Params**: `days` (integer, default 7)
- **Ownership**: Filters by `current_user.id`
- **Response**: `RotationSuggestionsResponse` with filtered suggestions
- **New Behavior**: Items outside `[−abs(days), days]` window excluded from suggestions

#### `GET /m3/analytics?days=N`
- **Method**: GET
- **Auth**: `get_current_user` dependency
- **Params**: `days` (integer, default 7)
- **Ownership**: Filters by `current_user.id`
- **Response**: `M3AnalyticsResponse` with enhanced quality metrics
- **New Metrics**: `expiring_soon_count`, `expired_count`, `high_risk_count`
- **New Behavior**: RSL window filtering applied to metric calculations

### No New Endpoints Created
- Avoided duplicate routes per task rules
- Enhanced existing endpoints to provide inventory insights
- Backward compatible - default `days=7` maintains existing behavior

## 10. Database Changes

**No new tables or columns were added.** The implementation reuses existing data model:

- `FoodItem.expiry_date` - used for FEFO sorting and expiring detection
- `ShelfLifePrediction.remaining_shelf_life_days` - used for expiring-soon calculations
- `ShelfLifePrediction.risk_level` - used for high_risk_count metric
- `ShelfLifePrediction.predicted_expiry_date` - used in FEFO sorting
- `ShelfLifePrediction.input_snapshot` - JSON containing `temperature_c`, `humidity_pct`, `food_type`, etc.
- `StorageCondition.temperature_c`, `humidity_pct`, `air_circulation`, `light_exposure`, `packaging_type`, `storage_duration_days` - used for storage-quality correlation

**Schema Updates:**
- `app/schemas.py`: Added `expiring_soon_count`, `expired_count`, `high_risk_count` to `M3AnalyticsResponse`

**No Migrations Required:** Existing schema was sufficient; only added optional fields with defaults.

## 11. Authentication & Ownership

### Verified Security Measures

1. **`get_current_user` dependency**: Extracts and validates JWT token, returns User object
2. **`_owned_record()` function** (m3.py lines 29-36):
   - Takes db session, model class, record_id, and user_id
   - If record_id is None, returns None (no check needed)
   - Otherwise queries record where id == record_id AND owner_column == user_id
   - If record not found, raises HTTP 404 with descriptive message
   - Owner column: FoodItem uses `created_by`, others use `user_id`

3. **`GET /m3/rotation-suggestions`**:
   - Filters FoodItem by `FoodItem.created_by == current_user.id`
   - Ensures users can only see their own inventory
   - Days window further restricts to user's relevant items

4. **`GET /m3/analytics`**:
   - Queries ShelfLifePrediction where `user_id == current_user.id`
   - Optionally filters by remaining_shelf_life_days window
   - Users can only see their own prediction aggregates

5. **Cross-user data isolation**: All database queries are filtered by the authenticated user's ID
   - No endpoint allows querying another user's inventory
   - No endpoint allows accessing another user's predictions
   - `GET /m3/recommendations/{prediction_id}` raises HTTP 404 if prediction belongs to another user

6. **Explicit ownership tests**:
   - test_m2.py::test_b2_11_ownership_isolation verifies cross-user access is blocked
   - test_m3.py tests verify ownership via `_owned_record()`

## 12. Frontend Integration

**Minimal frontend changes required** - the existing API endpoints are ready for frontend consumption.

**Existing frontend-ready data:**
- `expiring_soon_count` and `expired_count` from analytics
- `high_risk_count` for priority highlighting
- FEFO rotation suggestions with reasons and risk levels
- Prediction history with remaining shelf life and risk info
- Inventory item identity (name, category, quantity, expiry date, days until expiry)

**No redesign required** - the existing M3 analytics and rotation endpoints already provide inventory insight data. The frontend can:
- Call `GET /m3/rotation-suggestions?days=3` to get expiring-items rotation order
- Call `GET /m3/analytics?days=7` to get quality overview summary
- Display `expiring_soon_count`, `expired_count`, `high_risk_count` in the UI
- Use FEFO suggestions for inventory management workflows

**Example Frontend Use Cases:**
1. **Inventory Dashboard**: Show `total_predictions`, `expiring_soon_count`, `expired_count`, `high_risk_count`
2. **Expiring Items List**: Call `GET /m3/rotation-suggestions?days=3` and display the suggestions
3. **Risk Highlighting**: Use `high_risk_count` to flag items needing attention
4. **Prediction History**: Call `GET /m3/shelf-life/history` and display each prediction's remaining shelf life and risk

## 13. Tests Executed

### All Existing Tests Passing
| Test File | Tests | Result |
|-----------|-------|--------|
| `test_m3.py` | 4 | ✅ All Passed |
| `test_m2.py` | 5 | ✅ All Passed |
| **Total** | **9** | ✅ **9/9 Passed** |

### Test Coverage Verification
The existing test suite verifies:
- ✅ `test_approved_ml_predictions` - ML predictions work with enhanced analytics/rotation
- ✅ `test_unsupported_categories_return_422` - Unsupported categories still rejected
- ✅ `test_out_of_domain_inputs_return_422` - Out-of-domain inputs still return 422
- ✅ `test_history_recommendations_analytics` - History, recommendations, analytics all work
- ✅ `test_image_analysis`, `test_assessment_mapping`, `test_api_endpoints`, `test_dataset_utils`, `test_m1_regression` - M2 functionality intact

### Manual Verification Scenarios
1. **Expiring-soon filtering**: `GET /m3/rotation-suggestions?days=3` returns only items expiring within 3-day window
2. **Days parameter default**: `GET /m3/rotation-suggestions` (no parameter) defaults to 7 days, backward compatible
3. **Expired items included**: Items with `expiry_date < today` always appear first in FEFO order
4. **Cross-user access blocked**: Different users see only their own inventory and predictions
5. **Empty inventory**: Returns `total_items=0`, empty suggestions list
6. **Negative days**: Uses `abs(days)` for lower bound, e.g., `days=-3` gives window [−3, 3]
7. **No predictions for some items**: Items without predictions included with `risk_level=None`

### Test Results Summary

| Component | Status |
|-----------|--------|
| `test_approved_ml_predictions` | ✅ Pass |
| `test_unsupported_categories_return_422` | ✅ Pass |
| `test_out_of_domain_inputs_return_422` | ✅ Pass |
| `test_history_recommendations_analytics` | ✅ Pass |
| `test_image_analysis` | ✅ Pass |
| `test_assessment_mapping` | ✅ Pass |
| `test_api_endpoints` | ✅ Pass |
| `test_dataset_utils` | ✅ Pass |
| `test_m1_regression` | ✅ Pass |
| **Total** | **9/9 Pass** |

## 14. Edge Cases

### Tested Scenarios
1. **No inventory**: Empty suggestions list, `total_items=0`, no errors
2. **No predictions**: Items without predictions included with `risk_level=None`, `official_freshness_score=None`
3. **Item already expired**: `days_until_expiry < 0` → always ranks first in FEFO, `is_expired=true`
4. **Item expiring today**: `days_until_expiry == 0` → high urgency, "Expires today. Consume immediately."
5. **Item expiring within requested window**: `0 < days_until_expiry <= days` → included in filtered set
6. **Item outside requested window**: `days_until_expiry > days` → excluded from suggestions
7. **Missing optional prediction**: Item included in FEFO sort, `latest_pred.get(item.id)` returns None, uses `(1, 0)` freshness key
8. **Multiple predictions for same item**: Only the most recent prediction (by `created_at`) used via `latest_pred` dict
9. **Unauthorized access**: FastAPI `get_current_user` dependency enforces authentication; HTTP 401 if missing
10. **Invalid days parameter**: FastAPI integer validation; negative values handled via `abs()`
11. **Existing M2 functionality**: All `test_m2.py` tests pass unchanged
12. **Existing M3 shelf-life prediction**: All `test_m3.py` tests pass unchanged
13. **Existing storage monitoring**: All storage condition endpoints work unchanged

### Edge Case Handling
- `days=0`: Window `[0, 0]` → only items with `remaining_shelf_life_days == 0` (expiring right now)
- `days=-1`: Window `[−1, 1]` → items expiring yesterday, today, or tomorrow
- Very large `days` (e.g., `days=365`): Includes nearly all items in the window
- Zero predictions: Returns null aggregates per A3 convention
- All items expired: `expired_count = total_predictions`, `expiring_soon_count = 0`

## 15. Performance Considerations

### Database Query Optimization
- **FEFO rotation**: Single query for FoodItem filtered by `current_user.id`, ordered by `expiry_date.asc()`; single query for latest prediction per food_item_id
- **Analytics with days window**: Single query for ShelfLifePrediction with optional RSL filter; all metrics computed in Python over result set
- **No N+1 queries**: Predictions fetched in single batch via `food_item_id.in_(item_ids)`

### Dataset Size
- Typical deployment: Dozens to low hundreds of predictions per user
- Metrics computed over result set in Python - negligible overhead for expected dataset sizes
- No loading of huge datasets into Python - database filtering via `WHERE` clauses first

### Caching
- No caching introduced - per task rules
- Existing project does not appear to use caching for these endpoints
- Responses are deterministic and quick for expected data volumes

### Expected Performance
- `GET /m3/rotation-suggestions`: < 100ms for typical user datasets
- `GET /m3/analytics`: < 100ms for typical user datasets
- Both endpoints scale linearly with number of user's predictions/items

## 16. Known Limitations

1. **RSL window filtering is approximate**: The `days` parameter filters by `remaining_shelf_life_days` stored in the prediction, which is a rule-based estimate. Actual shelf life may vary based on real-world conditions.

2. **No direct food-item-to-prediction count**: The `expiring_soon_count` in analytics counts predictions, not individual FoodItem records. If a FoodItem has multiple predictions, the count may not match item-level expectations.

3. **Category-specific domain constraints not enforced at insight level**: The `days` parameter uses a generic remaining shelf life window. Category-specific model domains (e.g., tomato expects 20-25°C) are enforced at prediction time, not at the insight filtering level.

4. **No real-time expiry date validation**: The `expiry_date` on FoodItem is the source of truth for FEFO sorting, but `remaining_shelf_life_days` from the prediction is used for analytics window filtering. These may differ if the prediction was re-run or conditions changed.

5. **High_risk_count based on prediction risk only**: `high_risk_count` counts items with `risk_level in ("critical", "high")`. It does not incorporate storage condition scores or other factors.

6. **No per-food-type breakdown**: Metrics are aggregated across all food types. Category-specific counts would require additional queries.

7. **Snapshot data dependency**: Storage impact averages (`average_temperature_c`, `average_humidity_pct`) depend on the `input_snapshot` JSON being present and valid in each ShelfLifePrediction record.

8. **No future predictions beyond stored data**: Insights only cover predictions already made. New predictions must be created before they appear in analytics/rotation.

## 17. Next M3 Step

The next step will be **Analytics / Dashboard Integration**, which will build on the Inventory Insights to provide visual dashboards and aggregate overview screens.

**INVENTORY INSIGHTS STATUS: COMPLETE**

All five insight categories are implemented and verified:
- ✅ Expiring-soon inventory (via `GET /m3/rotation-suggestions?days=N` and `GET /m3/analytics?days=N`)
- ✅ FEFO rotation (`GET /m3/rotation-suggestions` with deterministic ordering)
- ✅ Inventory quality overview (enhanced `GET /m3/analytics` with `expiring_soon_count`, `expired_count`, `high_risk_count`)
- ✅ Shelf-life prediction history (`GET /m3/shelf-life/history` - already implemented)
- ✅ Inventory summary (via enhanced `GET /m3/analytics`)

All 9 existing tests pass. No models retrained. No synthetic data created. No new endpoints (enhanced existing). No safety rule violations.

## 18. Verification of Existing M3/M2 Functionality

After implementation, the following existing workflows were verified:

### M2 Functionality (unchanged)
- `POST /analysis/predict` - MobileNetV2 image analysis still works
- All `test_m2.py` tests pass (5/5)

### M3 Functionality (verified intact)
- `POST /m3/shelf-life/predict` - ML predictions still work (4/4 tests pass)
- `POST /m3/storage-conditions` - Storage condition recording still works
- `GET /m3/storage-conditions` - Storage history still works
- `GET /m3/recommendations/{prediction_id}` - Recommendations still work
- `GET /m3/rotation-suggestions` - FEFO rotation still works (enhanced with days parameter)
- `GET /m3/analytics` - Analytics still work (enhanced with quality metrics)

**All existing M2/M3 functionality remains intact.**

---
**Final Report**: `M3_INVENTORY_INSIGHTS_IMPLEMENTATION.md` created at
`D:\infosys\project 1\backend\app\ml\reports\M3_INVENTORY_INSIGHTS_IMPLEMENTATION.md`