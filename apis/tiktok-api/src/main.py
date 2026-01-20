"""
TikTok Ads -> BigQuery API (Cloud Run)

API para extração de dados de campanhas TikTok Ads e carga no BigQuery.
Suporta 4 níveis de relatório: advertiser, campaign, adgroup, ad.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Any

from flask import Flask, jsonify, request
from loguru import logger

from config.settings import (
    PROJECT_ID,
    DATASET_ID,
    TABLES,
    DEFAULT_DAYS_REPROCESS,
)
from controller.TikTokAdsController import TikTokAdsController
from database.BigQuery import BigQuery

app = Flask(__name__)


def get_required(payload: dict, key: str) -> Any:
    """Valida e retorna parâmetro obrigatório."""
    if key not in payload or payload[key] is None or payload[key] == "":
        raise ValueError(f"O parâmetro '{key}' é obrigatório.")
    return payload[key]


def get_optional(payload: dict, key: str, default: Any = None) -> Any:
    """Retorna parâmetro opcional com valor default."""
    value = payload.get(key)
    if value is None or value == "":
        return default
    return value


def get_env_int(*keys: str, default: int) -> int:
    """Retorna variável de ambiente como inteiro."""
    for k in keys:
        v = os.environ.get(k)
        if v is not None and str(v).strip() != "":
            return int(v)
    return default


def run_extraction(payload: dict) -> dict:
    """
    Executa extração de dados TikTok Ads para BigQuery.

    Args:
        payload: Parâmetros da requisição

    Returns:
        Resultado da execução
    """
    request_id = str(uuid.uuid4())
    logger.info(f"{request_id} - Iniciando extração TikTok Ads -> BigQuery")

    # Configurações de ambiente
    days_reprocess = get_env_int("DAYS_REPROCESS", default=DEFAULT_DAYS_REPROCESS)

    # Parâmetros obrigatórios
    access_token = get_required(payload, "access_token")
    advertiser_ids = get_required(payload, "advertiser_ids")

    # Parâmetros opcionais
    project_id = get_optional(payload, "project_id", PROJECT_ID)
    dataset_id = get_optional(payload, "dataset_id", DATASET_ID)
    if_exists = get_optional(payload, "if_exists", "append")

    # Tipos de relatório a extrair (default: todos)
    report_types = get_optional(
        payload, "report_types", ["advertiser", "campaign", "adgroup", "ad"]
    )

    # Datas
    start_date = get_optional(payload, "start_date", "")
    end_date = get_optional(payload, "end_date", "")

    # Normaliza advertiser_ids para lista
    if isinstance(advertiser_ids, str):
        advertiser_ids = [advertiser_ids]

    # Calcula datas padrão se não informadas
    if not start_date or not end_date:
        end_date_dt = datetime.utcnow() - timedelta(days=1)
        start_date_dt = end_date_dt - timedelta(days=days_reprocess - 1)
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")

    logger.info(f"{request_id} - Período: {start_date} a {end_date}")
    logger.info(f"{request_id} - Advertisers: {advertiser_ids}")
    logger.info(f"{request_id} - Report types: {report_types}")

    # Inicializa BigQuery
    bq = BigQuery(project_id=project_id)
    bq.auth()

    results = []

    for advertiser_id in advertiser_ids:
        advertiser_id = str(advertiser_id).replace("-", "").strip()
        logger.info(f"{request_id} - Processando advertiser: {advertiser_id}")

        for report_type in report_types:
            if report_type not in TABLES:
                logger.warning(f"Report type '{report_type}' não suportado. Ignorando.")
                continue

            table_name = TABLES[report_type]
            destination_table = f"{dataset_id}.{table_name}"

            logger.info(
                f"{request_id} - Extraindo {report_type} para {destination_table}"
            )

            try:
                # Inicializa controller TikTok
                tiktok = TikTokAdsController(
                    access_token=access_token,
                    advertiser_id=advertiser_id,
                    start_date=start_date,
                    end_date=end_date,
                    report_type=report_type,
                )

                # Extrai dados
                df = tiktok.fetch_report_retry()

                if df.empty:
                    logger.warning(
                        f"{request_id} - Sem dados para {report_type} "
                        f"(advertiser: {advertiser_id})"
                    )
                    results.append(
                        {
                            "advertiser_id": advertiser_id,
                            "report_type": report_type,
                            "destination_table": destination_table,
                            "inserted_rows": 0,
                            "status": "empty",
                        }
                    )
                    continue

                # Exporta para BigQuery
                inserted = bq.export(
                    df=df,
                    destination_table=destination_table,
                    start_date=start_date,
                    end_date=end_date,
                    advertiser_id=advertiser_id,
                    if_exists=if_exists,
                )

                results.append(
                    {
                        "advertiser_id": advertiser_id,
                        "report_type": report_type,
                        "destination_table": destination_table,
                        "inserted_rows": inserted,
                        "status": "success",
                    }
                )

            except Exception as e:
                logger.error(
                    f"{request_id} - Erro ao processar {report_type} "
                    f"(advertiser: {advertiser_id}): {e}"
                )
                results.append(
                    {
                        "advertiser_id": advertiser_id,
                        "report_type": report_type,
                        "destination_table": destination_table,
                        "inserted_rows": 0,
                        "status": "error",
                        "error": str(e),
                    }
                )

    # Sumariza resultado
    total_inserted = sum(r.get("inserted_rows", 0) for r in results)
    errors = [r for r in results if r.get("status") == "error"]

    return {
        "status": "Ok" if not errors else "Partial",
        "message": "Extração concluída",
        "request_id": request_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_inserted_rows": total_inserted,
        "results": results,
        "errors_count": len(errors),
    }


@app.get("/health")
def health():
    """Endpoint de health check."""
    return jsonify({"status": "ok", "service": "tiktok-ads-api"}), 200


@app.post("/run")
def run():
    """Endpoint principal para execução da extração."""
    payload = request.get_json(silent=True) or {}

    try:
        result = run_extraction(payload)
        status_code = 200 if result["status"] == "Ok" else 207
        return jsonify(result), status_code

    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 400

    except Exception as e:
        logger.exception(f"Execution error: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 500


def main():
    """Entry point para Cloud Run."""
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
