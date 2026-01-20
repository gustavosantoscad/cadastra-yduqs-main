"""
DAG Airflow para extração diária de dados TikTok Ads -> BigQuery

Orquestra a execução da API TikTok Ads no Cloud Run.
Utiliza Taskflow API para definição de tasks.

Autor: Data Engineering Team
Data: Janeiro 2025
"""

from datetime import datetime, timedelta
from typing import Any

from airflow.decorators import dag, task  # type: ignore
from airflow.models import Variable  # type: ignore
from google.auth.transport.requests import Request
from google.oauth2 import id_token
import requests
from loguru import logger

# Configurações da DAG
DAG_ID = "dag_tiktok_ads_to_bigquery"
SCHEDULE_INTERVAL = "0 8 * * *"  # Todos os dias às 08:00 UTC

# Configurações do Cloud Run
CLOUD_RUN_URL = Variable.get("TIKTOK_ADS_CLOUD_RUN_URL", default_var="")
GCP_PROJECT = Variable.get("GCP_PROJECT", default_var="cadastra-yducs-prod")
GCP_REGION = Variable.get("GCP_REGION", default_var="southamerica-east1")

# Credenciais TikTok (armazenadas como Variable ou Secret)
TIKTOK_ACCESS_TOKEN = Variable.get("TIKTOK_ACCESS_TOKEN", default_var="")
TIKTOK_ADVERTISER_IDS = Variable.get(
    "TIKTOK_ADVERTISER_IDS", 
    default_var="",
    deserialize_json=True
)


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "execution_timeout": timedelta(hours=2),
}


def get_oidc_token(target_audience: str) -> str:
    """
    Gera token OIDC para autenticação no Cloud Run privado.
    
    Args:
        target_audience: URL do serviço Cloud Run
        
    Returns:
        Token OIDC
    """
    auth_req = Request()
    token = id_token.fetch_id_token(auth_req, target_audience)
    return token


@dag(
    dag_id=DAG_ID,
    default_args=default_args,
    description="Extração diária de dados TikTok Ads para BigQuery",
    schedule_interval=SCHEDULE_INTERVAL,
    start_date=datetime(2025, 1, 1),
    catchup=False,
    max_active_runs=1,
    tags=["tiktok", "ads", "bigquery", "daily"],
)
def tiktok_ads_extraction():
    """
    Pipeline de extração TikTok Ads -> BigQuery.
    
    Flow:
    1. Valida configurações
    2. Prepara payload
    3. Executa API no Cloud Run
    4. Valida resultado
    """

    @task(task_id="validate_config")
    def validate_config() -> dict:
        """Valida se todas as configurações necessárias estão presentes."""
        errors = []

        if not CLOUD_RUN_URL:
            errors.append("TIKTOK_ADS_CLOUD_RUN_URL não configurada")

        if not TIKTOK_ACCESS_TOKEN:
            errors.append("TIKTOK_ACCESS_TOKEN não configurado")

        if not TIKTOK_ADVERTISER_IDS:
            errors.append("TIKTOK_ADVERTISER_IDS não configurado")

        if errors:
            raise ValueError(f"Configurações inválidas: {', '.join(errors)}")

        return {
            "cloud_run_url": CLOUD_RUN_URL,
            "advertiser_count": len(TIKTOK_ADVERTISER_IDS),
            "project": GCP_PROJECT,
        }

    @task(task_id="prepare_payload")
    def prepare_payload(config: dict, **context) -> dict:
        """
        Prepara payload para requisição à API.
        
        Calcula datas baseado na data de execução do DAG.
        """
        # Data de execução (D-1)
        execution_date = context["execution_date"]
        end_date = (execution_date - timedelta(days=1)).strftime("%Y-%m-%d")
        start_date = (execution_date - timedelta(days=3)).strftime("%Y-%m-%d")

        payload = {
            "access_token": TIKTOK_ACCESS_TOKEN,
            "advertiser_ids": TIKTOK_ADVERTISER_IDS,
            "project_id": GCP_PROJECT,
            "dataset_id": "RAW",
            "if_exists": "append",
            "report_types": ["advertiser", "campaign", "adgroup", "ad"],
            "start_date": start_date,
            "end_date": end_date,
        }

        return payload

    @task(task_id="call_cloud_run_api")
    def call_cloud_run_api(payload: dict) -> dict:
        """
        Chama a API TikTok Ads no Cloud Run.
        
        Utiliza autenticação OIDC para Cloud Run privado.
        """
        # Gera token OIDC
        token = get_oidc_token(CLOUD_RUN_URL)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        url = f"{CLOUD_RUN_URL}/run"

        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=600,  # 10 minutos
        )

        response.raise_for_status()
        result = response.json()

        return result

    @task(task_id="validate_result")
    def validate_result(result: dict) -> dict:
        """
        Valida resultado da extração.
        
        Lança exceção se houver erros críticos.
        """
        status = result.get("status", "Unknown")
        errors_count = result.get("errors_count", 0)
        total_rows = result.get("total_inserted_rows", 0)

        if status == "Error":
            raise Exception(f"Extração falhou: {result.get('message')}")

        if errors_count > 0:
            # Log warning mas não falha (alguns advertisers podem ter dados vazios)
            print(f"⚠️ {errors_count} erros durante extração")
            for r in result.get("results", []):
                if r.get("status") == "error":
                    print(f"  - {r.get('report_type')}: {r.get('error')}")

        summary = {
            "status": status,
            "total_rows_inserted": total_rows,
            "errors_count": errors_count,
            "request_id": result.get("request_id"),
            "period": f"{result.get('start_date')} to {result.get('end_date')}",
        }

        print(f"✅ Extração concluída: {total_rows} linhas inseridas")

        return summary

    # Define o fluxo de tasks
    config = validate_config()
    payload = prepare_payload(config)
    result = call_cloud_run_api(payload)
    summary = validate_result(result)


# Instancia a DAG
dag_instance = tiktok_ads_extraction()
