"""
Google Ads Controller - Extração de dados via GAQL.
"""
import re
from typing import Any, List, MutableMapping
import pandas as pd
from loguru import logger
from retry import retry

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.api_core.exceptions import InternalServerError, ServerError, TooManyRequests
from google.protobuf.json_format import MessageToDict


class GoogleAdsController:
    API_VERSION = "v20"

    def __init__(
        self,
        developer_token: str,
        refresh_token: str,
        client_id: str,
        client_secret: str,
        login_customer_id: str,
        customer_id: str,
        start_date: str,
        end_date: str,
        use_proto_plus: bool = False,
    ):
        self.credentials = {
            "developer_token": developer_token,
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "login_customer_id": str(login_customer_id).replace("-", ""),
            "use_proto_plus": str(use_proto_plus).lower(),
        }
        self.customer_id = str(customer_id).replace("-", "")
        self.start_date = start_date
        self.end_date = end_date
        self.client = None
        self.ga_service = None

    def auth(self):
        """Autentica com Google Ads API."""
        self.client = GoogleAdsClient.load_from_dict(self.credentials)
        self.ga_service = self.client.get_service("GoogleAdsService", version=self.API_VERSION)
        logger.info(f"Google Ads autenticado. Customer: {self.customer_id}")

    @staticmethod
    def camel_to_snake(name: str) -> str:
        """Converte camelCase para snake_case."""
        s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()

    def get_default_query(self) -> str:
        """Retorna query padrão para campanhas."""
        return f"""
            SELECT
                segments.date,
                customer.id,
                customer.descriptive_name,
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                ad_group.id,
                ad_group.name,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.video_views,
                metrics.engagements
            FROM campaign
            WHERE segments.date BETWEEN '{self.start_date}' AND '{self.end_date}'
        """

    @retry(
        exceptions=(InternalServerError, ServerError, TooManyRequests),
        tries=3,
        delay=30,
        backoff=2,
    )
    def request_report(self, query: str = None) -> pd.DataFrame:
        """
        Executa query GAQL e retorna DataFrame.
        
        Args:
            query: Query GAQL customizada (opcional)
        
        Returns:
            DataFrame com resultados
        """
        if query is None:
            query = self.get_default_query()

        logger.info(f"Executando query para customer_id={self.customer_id}")
        rows_list = []

        try:
            response_stream = self.ga_service.search_stream(
                customer_id=self.customer_id, query=query
            )

            for batch in response_stream:
                for row in batch.results:
                    row_json = MessageToDict(row)
                    rows_list.append(row_json)

            if not rows_list:
                logger.warning("Query retornou 0 resultados")
                return pd.DataFrame()

            df = pd.json_normalize(rows_list)
            df.columns = [self.camel_to_snake(c.replace(".", "_")) for c in df.columns]
            
            # Adiciona metadados
            df["account_id"] = self.customer_id
            
            # Converte cost_micros para valor real
            if "metrics_cost_micros" in df.columns:
                df["metrics_cost"] = df["metrics_cost_micros"].astype(float) / 1_000_000

            logger.success(f"Extraídos {len(df)} registros")
            return df

        except GoogleAdsException as ex:
            logger.error(f"GoogleAdsException: {ex.error.code().name}")
            for error in ex.failure.errors:
                logger.error(f"Erro: {error.message}")
            raise

    def request_report_retry(self, query: str = None) -> pd.DataFrame:
        """Alias com retry embutido."""
        return self.request_report(query)
