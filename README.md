# AI Food Freshness Monitoring Platform — Milestones 1–3

Milestone 1 implementation based on the provided Infosys project specification.

## Included
- Responsive React + JavaScript frontend
- Python + FastAPI backend
- PostgreSQL database
- Dynamic registration and login with JWT authentication
- Role selection during registration
- Food inventory workflow:
  - Add food
  - Store food in PostgreSQL
  - Retrieve inventory
  - Display inventory
  - Delete inventory item
- Docker Compose for frontend, backend and PostgreSQL
- M2 OpenCV visual analysis and MobileNetV2 freshness classification
- M3 ML-based shelf-life forecasting (category-specific regression for Tomato, Paneer, Seafood), storage monitoring, recommendations, and analytics

## Roles
- Consumer
- Retail Manager
- Warehouse Operator
- Food Quality Inspector
- Administrator

## Run with Docker

```bash
docker compose up --build
```

Frontend: http://localhost:5173  
Backend API docs: http://localhost:8000/docs

## Run backend locally

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend expects a PostgreSQL connection through DATABASE_URL.

## Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

The frontend uses VITE_API_URL (default: http://localhost:8000).

## M3 Shelf-Life Prediction Engine

M3 integrates trained, validated ML regression models for Remaining Shelf Life (RSL) inference, combined with contextual storage factor assessment and action recommendations:

- **Approved Production ML Categories:**
  - **Tomato:** `tomato_rsl.joblib` (RandomForestRegressor)
  - **Paneer:** `paneer_rsl.joblib` (LinearRegression)
  - **Seafood:** `seafood_rsl.joblib` (RandomForestRegressor; species: mackerel, tilapia, tuna)
- **Unsupported Categories:** Chicken, Avocado, Bakery, Packaged Foods, Beverages are strictly rejected with HTTP 422 to prevent out-of-domain errors.
- **Strict Domain Validation:** All input storage parameters (temperature, humidity, duration, packaging) undergo domain bounds validation before model inference.
- **Confidence Metric:** Explicitly set to `null` to maintain scientific integrity without uncalibrated heuristics.

The official freshness score combines multi-factor attributes:
```text
40% Visual Condition Analysis
+ 25% Storage Conditions
+ 20% Shelf-Life Prediction
+ 15% Product Age
```

M3 endpoints:

- `POST /m3/storage-conditions`
- `GET /m3/storage-conditions`
- `POST /m3/shelf-life/predict`
- `GET /m3/shelf-life/history`
- `GET /m3/recommendations/{prediction_id}`
- `GET /m3/analytics`
- `GET /m3/rotation-suggestions`

## Streamlit demo

`streamlit_app.py` is a status-only demo. It calls the separately hosted
FastAPI backend's `GET /health` endpoint; it does not implement the React
application's login, inventory, reporting, or M1–M4 workflows.

Run it locally from this repository root:

```powershell
python -m pip install -r requirements.txt
$env:API_BASE_URL = "http://localhost:8000"
python -m streamlit run streamlit_app.py
```

To deploy on Streamlit Community Cloud, select this repository and the
`demo/streamlit-status` branch, use `streamlit_app.py` as the entry point, and
configure the app secret below with the public HTTPS origin of a separately
hosted FastAPI backend:

```toml
API_BASE_URL = "https://your-fastapi-service.example.com"
```

Without that secret, the page honestly reports that the backend is not
configured. Streamlit Cloud does not host the FastAPI backend or persistent
database; do not use an ephemeral local database for persistent user records.
