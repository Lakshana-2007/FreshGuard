# FreshGuard

FreshGuard is a React/Vite web app with a FastAPI backend and PostgreSQL
persistence. It includes account registration and role-based access, inventory
management, image analysis, reports, storage monitoring, and shelf-life
prediction workflows.

## Local development

Install the backend dependencies from `backend/requirements.txt`, install the
frontend dependencies with `npm ci` from `frontend/`, and configure the values
shown in `.env.example`. Start the database and services with:

```sh
docker compose up --build
```

The frontend is served on port 3000, the API on port 8000, and the API
documentation at `/docs` on the API origin. Vite development mode uses
`http://127.0.0.1:8000` when `VITE_API_URL` is unset. Production builds must
set `VITE_API_URL` to the public HTTPS API origin.

## ML scope

The retained legacy image model recognizes six apple, banana, and orange labels;
it is not a general food freshness or food-safety classifier. The M2 v2 model
registry has no approved production models, so that workflow abstains with an
explanation. M3 has three traceable categories and five synthetic demonstration
categories. Synthetic outputs are not validated real-world shelf-life claims.

## Deployment

Read [DEPLOYMENT.md](DEPLOYMENT.md) for the current free-tier review, secure
configuration, hosting limits, and verification checklist. No cloud resources
have been created yet.
