"""
TikTok Ads API Controller
Responsável por autenticação e extração de relatórios da API TikTok Business
"""

import time
from datetime import datetime
from typing import Optional

import pandas as pd
import requests
from loguru import logger

from config.settings import (
    TIKTOK_API_BASE_URL,
    TIKTOK_REPORT_ENDPOINT,
    DIMENSIONS,
    DATA_LEVELS,
    METRICS,
)


class TikTokAdsController:
    """Controller para interação com TikTok Business API v1.3"""

    def __init__(
        self,
        access_token: str,
        advertiser_id: str,
        start_date: str,
        end_date: str,
        report_type: str = "campaign",
    ):
        """
        Inicializa o controller.

        Args:
            access_token: Token de acesso da API TikTok
            advertiser_id: ID do anunciante
            start_date: Data inicial (YYYY-MM-DD)
            end_date: Data final (YYYY-MM-DD)
            report_type: Tipo de relatório (advertiser, campaign, adgroup, ad)
        """
        self.access_token = access_token
        self.advertiser_id = str(advertiser_id).replace("-", "").strip()
        self.start_date = start_date
        self.end_date = end_date
        self.report_type = report_type
        self.base_url = TIKTOK_API_BASE_URL
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    def _get_dimensions(self) -> list:
        """Retorna as dimensões para o tipo de relatório."""
        return DIMENSIONS.get(self.report_type, DIMENSIONS["campaign"])

    def _get_data_level(self) -> str:
        """Retorna o data_level para o tipo de relatório."""
        return DATA_LEVELS.get(self.report_type, DATA_LEVELS["campaign"])

    def _get_metrics(self) -> list:
        """Retorna lista de métricas a serem extraídas."""
        return METRICS

    def _build_report_payload(self, page: int = 1, page_size: int = 1000) -> dict:
        """
        Constrói o payload para requisição de relatório.

        Args:
            page: Número da página
            page_size: Tamanho da página

        Returns:
            Payload formatado para a API
        """
        return {
            "advertiser_id": self.advertiser_id,
            "report_type": "BASIC",
            "data_level": self._get_data_level(),
            "dimensions": self._get_dimensions(),
            "metrics": self._get_metrics(),
            "start_date": self.start_date,
            "end_date": self.end_date,
            "page": page,
            "page_size": page_size,
            "filtering": [],
        }

    def _make_request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        max_retries: int = 3,
    ) -> dict:
        """
        Realiza requisição à API com retry.

        Args:
            endpoint: Endpoint da API
            method: Método HTTP
            params: Query parameters
            json_data: Body JSON
            max_retries: Número máximo de tentativas

        Returns:
            Resposta da API em JSON
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url,
                        headers=self.headers,
                        params=params,
                        timeout=120,
                    )
                else:
                    response = requests.post(
                        url,
                        headers=self.headers,
                        json=json_data,
                        timeout=120,
                    )

                response.raise_for_status()
                data = response.json()

                # Verifica código de erro da API TikTok
                if data.get("code") != 0:
                    error_msg = data.get("message", "Unknown error")
                    logger.warning(
                        f"TikTok API error (attempt {attempt + 1}): {error_msg}"
                    )

                    # Rate limit - aguarda e tenta novamente
                    if data.get("code") == 40100:
                        wait_time = 60 * (attempt + 1)
                        logger.info(f"Rate limit hit. Waiting {wait_time}s...")
                        time.sleep(wait_time)
                        continue

                    if attempt < max_retries - 1:
                        time.sleep(5 * (attempt + 1))
                        continue
                    raise Exception(f"TikTok API error: {error_msg}")

                return data

            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise

        raise Exception(f"Max retries ({max_retries}) exceeded")

    def fetch_report(self) -> pd.DataFrame:
        """
        Extrai relatório completo com paginação.

        Returns:
            DataFrame com todos os dados do relatório
        """
        logger.info(
            f"Fetching {self.report_type} report for advertiser {self.advertiser_id}"
        )
        logger.info(f"Period: {self.start_date} to {self.end_date}")

        all_data = []
        page = 1
        page_size = 1000
        total_pages = 1

        while page <= total_pages:
            logger.info(f"Fetching page {page}/{total_pages}")

            payload = self._build_report_payload(page=page, page_size=page_size)
            response = self._make_request(
                endpoint=TIKTOK_REPORT_ENDPOINT,
                method="GET",
                params={
                    "advertiser_id": self.advertiser_id,
                    "report_type": "BASIC",
                    "data_level": self._get_data_level(),
                    "dimensions": str(self._get_dimensions()),
                    "metrics": str(self._get_metrics()),
                    "start_date": self.start_date,
                    "end_date": self.end_date,
                    "page": page,
                    "page_size": page_size,
                },
            )

            data = response.get("data", {})
            rows = data.get("list", [])
            page_info = data.get("page_info", {})

            if rows:
                all_data.extend(rows)

            total_pages = page_info.get("total_page", 1)
            page += 1

            # Pequena pausa para evitar rate limit
            time.sleep(0.5)

        logger.info(f"Total records fetched: {len(all_data)}")

        if not all_data:
            logger.warning("No data returned from API")
            return pd.DataFrame()

        return self._parse_response(all_data)

    def _parse_response(self, data: list) -> pd.DataFrame:
        """
        Converte resposta da API em DataFrame.

        Args:
            data: Lista de registros da API

        Returns:
            DataFrame formatado
        """
        if not data:
            return pd.DataFrame()

        records = []
        for row in data:
            record = {}

            # Extrai dimensões
            dimensions = row.get("dimensions", {})
            for key, value in dimensions.items():
                record[key] = value

            # Extrai métricas
            metrics = row.get("metrics", {})
            for key, value in metrics.items():
                # Converte valores numéricos
                if value is not None and value != "":
                    try:
                        if "." in str(value):
                            record[key] = float(value)
                        else:
                            record[key] = int(value) if str(value).isdigit() else value
                    except (ValueError, TypeError):
                        record[key] = value
                else:
                    record[key] = None

            records.append(record)

        df = pd.DataFrame(records)

        # Adiciona metadados
        df["_advertiser_id"] = self.advertiser_id
        df["_extracted_at"] = datetime.utcnow().isoformat()
        df["_report_type"] = self.report_type

        # Renomeia stat_time_day para date se existir
        if "stat_time_day" in df.columns:
            df["date"] = pd.to_datetime(df["stat_time_day"]).dt.date
            df["date"] = df["date"].astype(str)

        logger.info(f"Parsed {len(df)} records into DataFrame")
        return df

    def fetch_report_retry(self, max_retries: int = 3) -> pd.DataFrame:
        """
        Extrai relatório com retry em caso de falha.

        Args:
            max_retries: Número máximo de tentativas

        Returns:
            DataFrame com dados do relatório
        """
        for attempt in range(max_retries):
            try:
                return self.fetch_report()
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 30 * (attempt + 1)
                    logger.info(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    raise

        return pd.DataFrame()
