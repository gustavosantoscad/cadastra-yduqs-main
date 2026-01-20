"""
Bing Ads -> BigQuery API (Cloud Run)
"""
import os
import sys
import uuid
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from loguru import logger

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller import BingAdsController
from shared.bigquery import BigQuery

app = Flask(__name__)


def get_required(payload: dict, key: str):
    if key not in payload or payload[key] is None or payload[key] == "":
        raise ValueError(f"Parâmetro '{key}' é obrigatório.")
    return payload[key]


def get_env_int(key: str, default: int) -> int:
    v = os.environ.get(key)
    return int(v) if v else default


def run_job(payload: dict) -> dict:
    req_id = str(uuid.uuid4())
    logger.info(f"{req_id} - Iniciando extração Bing Ads -> BigQuery")

    days_reprocess = get_env_int("DAYS_REPROCESS", 3)

    # Parâmetros obrigatórios
    project_id = get_required(payload, "project_id")
    destination_table = get_required(payload, "destination_table")
    if_exists = payload.get("if_exists", "append")

    developer_token = get_required(payload, "developer_token")
    client_id = get_required(payload, "client_id")
    client_secret = get_required(payload, "client_secret")
    refresh_token = get_required(payload, "refresh_token")
    customer_id = get_required(payload, "customer_id")
    account_ids = get_required(payload, "account_ids")

    # Opcionais
    report_type = payload.get("report_type", "CampaignPerformanceReport")
    columns = payload.get("columns")

    start_date = payload.get("start_date") or ""
    end_date = payload.get("end_date") or ""

    if isinstance(account_ids, str):
        account_ids = [account_ids]

    # Janela padrão
    if not start_date or not end_date:
        start_date_dt = datetime.utcnow() - timedelta(days=days_reprocess)
        end_date_dt = datetime.utcnow() - timedelta(days=1)
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")

    # BigQuery
    bq = BigQuery(credentials_path=None, project_id=project_id)
    bq.auth()

    results = []
    for aid in account_ids:
        account_id = str(aid)

        logger.info(f"{req_id} - Processando account_id={account_id}")

        bing = BingAdsController(
            developer_token=developer_token,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            account_id=account_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            report_type=report_type,
        )
        bing.auth()

        df = bing.request_report_retry(columns=columns)

        if df.empty:
            results.append({"account_id": account_id, "inserted_rows": 0})
            continue

        date_col = "date" if "date" in df.columns else "timeperiod"

        inserted = bq.export(
            df=df,
            start_date=start_date,
            end_date=end_date,
            destination_table=destination_table,
            project_id=project_id,
            if_exists=if_exists,
            account_id=account_id,
            date_column=date_col,
        )

        results.append({"account_id": account_id, "inserted_rows": inserted})

    return {
        "status": "Ok",
        "message": "Bing Ads data loaded",
        "request_id": req_id,
        "start_date": start_date,
        "end_date": end_date,
        "results": results,
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "bing-ads"}), 200


@app.post("/run")
def run():
    payload = request.get_json(silent=True) or {}
    try:
        resp = run_job(payload)
        return jsonify(resp), 200
    except Exception as e:
        logger.exception(f"Erro: {e}")
        return jsonify({"status": "Error", "message": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
