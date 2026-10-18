# FreshGuard deployment plan

## What is required

FreshGuard is a React/Vite frontend and a FastAPI backend. The backend includes
PyTorch, OpenCV, scikit-learn, eight enabled shelf-life model artifacts, and a 10 MB
MobileNetV2 checkpoint. A small 512 MB free web-service instance is not a safe
target for this runtime. Render's free web service has 0.1 CPU and 512 MB RAM,
sleeps after 15 minutes without traffic, and its free PostgreSQL expires after
30 days. Do not deploy this application there as a persistent production app.

The current zero-hosting-cost candidate is:

- **Compute:** Oracle Cloud Infrastructure Always Free Ampere A1 VM, within the
  current free-account allowance of 2 OCPUs and 12 GB RAM. It can keep the API
  and PostgreSQL running without an idle-sleep limit. The free allowance
  includes up to 200 GB of block storage. Only create resources marked Always
  Free; do not upgrade the account or use trial-credit resources.
- **Database:** Neon Free PostgreSQL, with 1 GB storage per project, 100
  compute-unit hours per month, scale-to-zero, and a six-hour instant-restore
  window. This is suitable for a demo, not a backup guarantee. Export regular
  `pg_dump` backups to storage outside Neon and periodically verify a restore.
- **Frontend:** Serve the built React app from the same VM behind a TLS reverse
  proxy, or use a free static host if its account and bandwidth limits fit.
  The API must be exposed over HTTPS and CORS must list the final frontend
  origin exactly.

Oracle's Always Free program requires account signup; Oracle says most signups
need a phone number and payment card, but the card is not charged unless the
account is upgraded. Always Free capacity can be unavailable in some regions.
The free account must be used at least once within 60 days to remain active.
Neon's Free plan is capped; monitor compute and storage so the database does
not become unavailable after limits are reached.

## Free-hosting review

| Provider | Relevant free limit | Decision |
| --- | --- | --- |
| Render | Web service: 0.1 CPU, 512 MB RAM; sleeps after 15 idle minutes. Free PostgreSQL: 1 GB and expires after 30 days, with no backups. | Reject for the full model runtime and durable app data. Static sites remain an option. |
| Neon | 1 GB database, 100 CU-hours per project/month, scale-to-zero, 10 branches. | Selected for managed PostgreSQL; export backups separately. |
| Hugging Face Spaces | CPU Basic: 2 vCPU, 16 GB RAM, 50 GB ephemeral disk, sleeps after 48 hours idle. Creating a Docker/Gradio compute Space requires a paid plan. | Not zero-cost for this Docker backend. |
| OCI Always Free A1 | Free account allowance: 2 OCPUs, 12 GB RAM and 200 GB block storage, within Always Free limits. | Candidate for persistent CPU ML runtime; account and ARM64 deployment still need owner-side verification. |

Limits checked against provider documentation on 2026-10-18. Provider terms and
availability can change. Sources:

- [Render free services and database limitations](https://render.com/docs/free)
- [Render compute plans](https://render.com/docs/compute-plans)
- [Neon Free plan update, October 2, 2026](https://neon.com/blog/neon-free-plan-1-gb-per-project)
- [Hugging Face Spaces hardware and sleep behavior](https://huggingface.co/docs/hub/spaces-gpus)
- [OCI Always Free resources](https://docs.oracle.com/en-us/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm)
- [OCI account behavior after the free promotion](https://docs.oracle.com/en-us/iaas/Content/GSG/Tasks/signingup_topic-What_Happens_When_the_Promotion_Expires.htm)

## Environment variables

Set these only in the hosting provider's secret/configuration interface:

| Name | Where | Value |
| --- | --- | --- |
| `DATABASE_URL` | Backend | Neon pooled PostgreSQL URL using `postgresql+psycopg://`; require SSL and URL-encode special characters in credentials. |
| `JWT_SECRET` | Backend | Fresh random value of at least 32 random bytes. Generate in the provider's secure console or on the VM and enter directly into the secret store. |
| `CORS_ORIGINS` | Backend | Comma-separated exact HTTPS frontend origin(s), no trailing slash. |
| `VITE_API_URL` | Frontend build | Public HTTPS API origin, no trailing slash. This is embedded at build time. |
| `PORT` | Backend container | The platform-provided port; the Docker command uses this value and falls back to 8000 for local Compose. |

Do not place production secrets in `.env.example`, Git, build arguments, or
logs. The checked-in `.env.example` contains development placeholders only.

## Build and run

The clean deployment repository has `backend/`, `frontend/`, and
`docker-compose.yml` at its root.

```sh
# Build React assets with the public API origin
cd frontend
npm ci
VITE_API_URL=https://api.example.invalid npm run build
cd ..

# Backend image: installs CPU-only PyTorch and production dependencies
docker build --platform linux/arm64 -t freshguard-api:deploy ./backend

# Local full-stack development; create a private .env from the template first
docker compose up --build
```

For a VM deployment, use a persistent PostgreSQL service or the managed Neon
database; never keep user data in the container filesystem. Configure TLS at a
reverse proxy, restrict inbound firewall rules to SSH and HTTPS, and expose
PostgreSQL only through Neon. Configure Neon with its pooled SSL connection
string. Keep the app's data path on the model files in
`backend/app/ml/saved_models/`.

## Model and operational limits

- The deployment keeps the legacy 10 MB freshness model and the M3 shelf-life
  models. It excludes unapproved candidate checkpoints and training datasets.
- The M2 v2 approval registry currently has no approved models. Its workflow
  must continue to abstain and explain that no approved model is available;
  this deployment does not fabricate predictions.
- The legacy MobileNetV2 model was trained for six apple, banana, and orange
  labels. It is not a general food freshness or food-safety classifier.
- Synthetic M3 category models remain labeled synthetic. Their results are
  demonstrations, not validated shelf-life claims.
- The backend Dockerfile supports x86_64 and arm64 CPU PyTorch wheels, but the
  arm64 image and inference path have not been built or tested yet.

## Verification status

No cloud resource or public URL has been created. The following remain
**NOT TESTED** until deployment: image build and startup on arm64, API health,
database connectivity, frontend page load, CORS, registration/login, role
authorization, inventory persistence, image upload, M2 abstention behavior,
M3 supported categories, error handling, and restart/backup restore.

After provisioning, run these checks using a fresh test account and synthetic
inputs only:

1. `GET https://<api-origin>/health` and `/docs`.
2. Open the frontend and confirm its browser network panel calls the configured
   API origin without CORS errors.
3. Register/login, verify an authorized request and a forbidden role request.
4. Create, list, update, and delete inventory data; confirm it remains after an
   API restart.
5. Test valid and invalid image files, then check both supported and unsupported
   shelf-life categories.
6. Restart the VM and services; verify PostgreSQL data and restore a recent
   `pg_dump` into a separate test database.

## Redeploy and rollback

Deploy a reviewed commit from `deploy/freshguard-free`. To roll back the app,
redeploy the preceding verified container/image or Git commit. Do not roll the
database schema back by deleting data; take a database export before applying
any migration. For Neon, export before changing plan or deleting the project.

## Current blockers

- GitHub could not be reached from the deployment environment, so the latest
  remote `main` and remote `deploy/freshguard` branch have not been verified.
- Cloud accounts and credentials are not connected. OCI signup, domain/TLS
  setup, Neon project creation, and public publication require the owner's
  account session.
- No ARM64 build was performed here. Do not call the app deployed until the
  verification checklist above passes against public URLs.
