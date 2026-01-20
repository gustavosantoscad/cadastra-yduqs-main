# Cloud Run - LinkedIn Ingestion API (Landing Zone)

Pipelines (Airflow orchestrates):

- `POST /ingest/lgeneral` -> `LANDING_ZONE.LN_LINKEDIN_GENERAL`
- `POST /ingest/lposts` -> `LANDING_ZONE.LN_LINKEDIN_POSTS` + `LANDING_ZONE.LN_ANALYTICS_METRICS`

Writes are idempotent via staging tables + MERGE into partitioned tables.

## Environment variables

Required:
- `GOOGLE_CLOUD_PROJECT` (or `GCP_PROJECT`)
- `LINKEDIN_CLIENT_NAME` (must match LinkedIn org localized name in admin ACL response)

Optional (defaults shown):
- `BQ_DATASET=LANDING_ZONE`
- `BQ_TABLE_GENERAL=LN_LINKEDIN_GENERAL`
- `BQ_TABLE_POSTS=LN_LINKEDIN_POSTS`
- `BQ_TABLE_METRICS=LN_ANALYTICS_METRICS`
- `LINKEDIN_TOKEN_SECRET=linkedin_api`
- `LINKEDIN_TOKEN_SECRET_VERSION=latest`
- `LINKEDIN_ORG_URN=urn:li:organization:511241`
- `LINKEDIN_ORG_URN_ENCODED=urn%3Ali%3Aorganization%3A511241`
- `LINKEDIN_POSTS_COUNT=40`
- `LOG_LEVEL=INFO`

## One-time table creation

Call (IAM-protected):
- `POST /admin/ensure-tables`

## Deploy (example)

```bash
gcloud run deploy linkedin-ingest \
  --source . \
  --region us-central1 \
  --no-allow-unauthenticated \
  --set-env-vars BQ_DATASET=LANDING_ZONE,LINKEDIN_CLIENT_NAME="Your Org Name"
```

## Airflow

See `airflow_dag_example.py`.
