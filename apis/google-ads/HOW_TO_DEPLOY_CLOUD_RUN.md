# Google Ads -> BigQuery API (Cloud Run, Private)

This project exposes a private HTTP API on Cloud Run that:

1) Pulls daily campaign metrics from Google Ads (GAQL),
2) Writes results into BigQuery (dataset.table).

## Endpoints

- `GET /health` -> healthcheck
- `POST /run` -> runs the extraction + load

## Authentication (Private Cloud Run)

Deploy with `--no-allow-unauthenticated` and grant `roles/run.invoker` to callers.
Calls must include an OIDC ID token:

```
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" "$URL/health"
```

## Request payload (POST /run)

```json
{
  "project_id": "my-gcp-project",
  "destination_table": "my_dataset.my_table",
  "if_exists": "append",
  "developer_token": "...",
  "refresh_token": "...",
  "client_id": "...",
  "client_secret": "...",
  "use_proto_plus": true,
  "login_customer_id": "1234567890",
  "customer_ids": ["1111111111", "2222222222"],
  "start_date": "2026-01-01",
  "end_date": "2026-01-07"
}
```

If `start_date/end_date` are omitted, the service uses a default window based on `days_reprocess` env var (default: 3).

## BigQuery table creation behavior

- The **dataset must exist** (recommended to create via Terraform/IaC).
- If the **table does not exist**, `pandas_gbq.to_gbq()` will create it automatically.
- If the table exists, the service deletes the date range for that `customer_id` before inserting.

To auto-create the dataset too, set:

- `AUTO_CREATE_DATASET=true`
- `BQ_DATASET_LOCATION=US` (or `southamerica-east1`-compatible region if desired)

## Build & Deploy (Windows PowerShell, Cloud Build)

From the folder that contains `Dockerfile`:

```powershell
$PROJECT="SEU_PROJETO"
$REGION="southamerica-east1"
$REPO="api-repo"
$SERVICE="minha-api"
$TAG="1.0.0"
$IMAGE="$REGION-docker.pkg.dev/$PROJECT/$REPO/$SERVICE`:$TAG"
$SA="SUA_SA@SEU_PROJETO.iam.gserviceaccount.com"

gcloud config set project $PROJECT
gcloud config set run/region $REGION
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

gcloud artifacts repositories create $REPO --repository-format=docker --location $REGION
gcloud builds submit --tag $IMAGE

gcloud run deploy $SERVICE `
  --image $IMAGE `
  --no-allow-unauthenticated `
  --service-account $SA `
  --port 8080 `
  --region $REGION `
  --set-env-vars ENV=prod,days_reprocess=3
```

## Local run (optional)

```
pip install -r requirements.txt
set PORT=8080
python main.py
```

(For local testing you may need local credentials with access to Google Ads and BigQuery.)
