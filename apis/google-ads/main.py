"""
Google Ads -> BigQuery API (Cloud Run)
"""
import os
import sys
import uuid
from datetime import datetime, timedelta

from flask import Flask, jsonify, request
from loguru import logger

# Adiciona shared ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from controller import GoogleAdsController
from shared.bigquery import BigQuery

app = Flask(__name__)


def get_required(payload: dict, key: str):
    if key not in payload or payload[key] is None or payload[key] == "":
        raise ValueError(f"Parâmetro '{key}' é obrigatório.")
    return payload[key]


def get_env_int(*keys: str, default: int) -> int:
    for k in keys:
        v = os.environ.get(k)
        if v is not None and str(v).strip() != "":
            return int(v)
    return default


def run_job(payload: dict) -> dict:
    req_id = str(uuid.uuid4())
    logger.info(f"{req_id} - Iniciando extração Google Ads -> BigQuery")

    days_reprocess = get_env_int("DAYS_REPROCESS", default=3)

    # Parâmetros obrigatórios
    project_id = get_required(payload, "project_id")
    destination_table = get_required(payload, "destination_table")
    if_exists = payload.get("if_exists", "append")

    developer_token = get_required(payload, "developer_token")
    refresh_token = get_required(payload, "refresh_token")
    client_id = get_required(payload, "client_id")
    client_secret = get_required(payload, "client_secret")
    login_customer_id = get_required(payload, "login_customer_id")
    customer_ids = get_required(payload, "customer_ids")

    # Query customizada (opcional)
    custom_query = payload.get("query")

    # Datas opcionais
    start_date = payload.get("start_date") or ""
    end_date = payload.get("end_date") or ""

    if isinstance(customer_ids, str):
        customer_ids = [customer_ids]

    # Janela padrão
    if not start_date or not end_date:
        start_date_dt = datetime.utcnow() - timedelta(days=days_reprocess)
        end_date_dt = datetime.utcnow() - timedelta(days=1)
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")

    # BigQuery via ADC
    bq = BigQuery(credentials_path=None, project_id=project_id)
    bq.auth()

    results = []
    for cid in customer_ids:
        customer_id = str(cid).replace("-", "").replace(" ", "")

        logger.info(f"{req_id} - Processando customer_id={customer_id}")
        
        ga = GoogleAdsController(
            developer_token=developer_token,
            refresh_token=refresh_token,
            client_id=client_id,
            client_secret=client_secret,
            login_customer_id=login_customer_id,
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
        )
        ga.auth()

        # Usa query customizada ou padrão
        if custom_query:
            query = custom_query
            if "segments.date" not in query.lower():
                where_clause = "AND" if "WHERE" in query.upper() else "WHERE"
                query += f" {where_clause} segments.date BETWEEN '{start_date}' AND '{end_date}'"
        else:
            query = None

        df = ga.request_report_retry(query)

        if df.empty:
            results.append({"customer_id": customer_id, "inserted_rows": 0})
            continue

        # Garante coluna de data para deleção
        date_col = "segments_date" if "segments_date" in df.columns else "date"

        inserted = bq.export(
            df=df,
            start_date=start_date,
            end_date=end_date,
            destination_table=destination_table,
            project_id=project_id,
            if_exists=if_exists,
            account_id=customer_id,
            date_column=date_col,
        )

        results.append({"customer_id": customer_id, "inserted_rows": inserted})

    return {
        "status": "Ok",
        "message": "Google Ads data loaded",
        "request_id": req_id,
        "start_date": start_date,
        "end_date": end_date,
        "results": results,
    }


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "google-ads"}), 200


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
