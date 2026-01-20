"""
DV360 (Display & Video 360) Controller.
"""
import io
import time
from typing import List, Optional, Dict, Any
import pandas as pd
from loguru import logger
from retry import retry
import requests

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


class DV360Controller:
    API_VERSION = "v2"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        partner_id: str,
        advertiser_id: str,
        start_date: str,
        end_date: str,
        query_id: str = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.partner_id = str(partner_id)
        self.advertiser_id = str(advertiser_id)
        self.start_date = start_date
        self.end_date = end_date
        self.query_id = query_id
        self.credentials = None
        self.service = None

    def auth(self):
        """Autentica com DV360 API."""
        self.credentials = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        self.service = build(
            "doubleclickbidmanager",
            self.API_VERSION,
            credentials=self.credentials,
        )
        logger.info(f"DV360 autenticado. Advertiser: {self.advertiser_id}")

    def get_default_query_spec(self) -> Dict[str, Any]:
        """Retorna spec padrão para query."""
        return {
            "dataRange": {
                "range": "CUSTOM_DATES",
                "customStartDate": {
                    "year": int(self.start_date[:4]),
                    "month": int(self.start_date[5:7]),
                    "day": int(self.start_date[8:10]),
                },
                "customEndDate": {
                    "year": int(self.end_date[:4]),
                    "month": int(self.end_date[5:7]),
                    "day": int(self.end_date[8:10]),
                },
            },
            "dimensions": [
                "FILTER_DATE",
                "FILTER_ADVERTISER",
                "FILTER_ADVERTISER_NAME",
                "FILTER_INSERTION_ORDER",
                "FILTER_INSERTION_ORDER_NAME",
                "FILTER_LINE_ITEM",
                "FILTER_LINE_ITEM_NAME",
                "FILTER_CREATIVE",
                "FILTER_CREATIVE_NAME",
            ],
            "metrics": [
                "METRIC_IMPRESSIONS",
                "METRIC_CLICKS",
                "METRIC_TOTAL_MEDIA_COST_USD_MICROS",
                "METRIC_TOTAL_CONVERSIONS",
                "METRIC_POST_VIEW_CONVERSIONS",
                "METRIC_POST_CLICK_CONVERSIONS",
                "METRIC_REVENUE_USD_MICROS",
                "METRIC_VIDEO_VIEWS",
                "METRIC_VIDEO_COMPLETIONS",
            ],
            "filters": [
                {
                    "type": "FILTER_ADVERTISER",
                    "value": self.advertiser_id,
                }
            ],
        }

    @retry(tries=3, delay=60, backoff=2)
    def request_report(self, query_spec: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Executa relatório no DV360.
        
        Args:
            query_spec: Especificação da query (opcional)
        
        Returns:
            DataFrame com resultados
        """
        if query_spec is None:
            query_spec = self.get_default_query_spec()

        logger.info(f"Iniciando extração DV360 advertiser_id={self.advertiser_id}")

        # Usa query existente ou cria nova
        if self.query_id:
            query_resource = self.service.queries().get(queryId=self.query_id).execute()
            logger.info(f"Usando query existente: {self.query_id}")
        else:
            # Cria query
            query_body = {
                "metadata": {
                    "title": f"API Export {self.advertiser_id}",
                    "dataRange": query_spec["dataRange"],
                    "format": "CSV",
                },
                "params": {
                    "type": "STANDARD",
                    "groupBys": query_spec["dimensions"],
                    "metrics": query_spec["metrics"],
                    "filters": query_spec.get("filters", []),
                },
                "schedule": {"frequency": "ONE_TIME"},
            }

            query_resource = self.service.queries().create(body=query_body).execute()
            self.query_id = query_resource["queryId"]
            logger.info(f"Query criada: {self.query_id}")

        # Executa query
        self.service.queries().run(queryId=self.query_id).execute()

        # Aguarda conclusão
        report_url = self._wait_for_report()

        if not report_url:
            logger.warning("Nenhum relatório gerado")
            return pd.DataFrame()

        # Download do relatório
        df = self._download_report(report_url)

        # Padroniza colunas
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # Adiciona metadados
        df["account_id"] = self.advertiser_id

        # Converte valores em micros
        for col in df.columns:
            if "micros" in col.lower():
                df[col.replace("_micros", "")] = df[col].astype(float) / 1_000_000

        # Renomeia data
        if "date" in df.columns:
            pass
        elif "filter_date" in df.columns:
            df["date"] = df["filter_date"]

        logger.success(f"Extraídos {len(df)} registros do DV360")
        return df

    def _wait_for_report(self, max_wait: int = 600) -> Optional[str]:
        """Aguarda relatório ficar pronto."""
        waited = 0
        interval = 30

        while waited < max_wait:
            reports = (
                self.service.queries()
                .reports()
                .list(queryId=self.query_id, orderBy="metadata.reportDataEndDate desc")
                .execute()
            )

            if reports.get("reports"):
                latest = reports["reports"][0]
                status = latest.get("metadata", {}).get("status", {}).get("state")

                if status == "DONE":
                    return latest.get("metadata", {}).get("googleCloudStoragePath")
                elif status == "FAILED":
                    logger.error("Relatório falhou")
                    return None

            time.sleep(interval)
            waited += interval
            logger.info(f"Aguardando relatório... {waited}s")

        logger.error("Timeout aguardando relatório")
        return None

    def _download_report(self, url: str) -> pd.DataFrame:
        """Faz download do relatório CSV."""
        response = requests.get(url)
        response.raise_for_status()
        return pd.read_csv(io.StringIO(response.text))

    def request_report_retry(self, query_spec: Dict[str, Any] = None) -> pd.DataFrame:
        """Alias com retry embutido."""
        return self.request_report(query_spec)
