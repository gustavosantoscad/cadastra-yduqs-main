"""
Bing Ads (Microsoft Advertising) Controller.
"""
import time
from typing import List, Optional
import pandas as pd
from loguru import logger
from retry import retry

from bingads.service_client import ServiceClient
from bingads.authorization import AuthorizationData, OAuthDesktopMobileAuthCodeGrant
from bingads.v13.reporting import ReportingServiceManager, ReportingDownloadParameters


class BingAdsController:
    REPORT_AGGREGATION = "Daily"
    TIMEOUT_IN_MILLISECONDS = 3600000

    def __init__(
        self,
        developer_token: str,
        client_id: str,
        client_secret: str,
        refresh_token: str,
        account_id: str,
        customer_id: str,
        start_date: str,
        end_date: str,
        report_type: str = "CampaignPerformanceReport",
    ):
        self.developer_token = developer_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.account_id = str(account_id)
        self.customer_id = str(customer_id)
        self.start_date = start_date
        self.end_date = end_date
        self.report_type = report_type
        self.authorization_data = None
        self.reporting_service_manager = None

    def auth(self):
        """Autentica com Bing Ads API."""
        authentication = OAuthDesktopMobileAuthCodeGrant(
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        authentication.request_oauth_tokens_by_refresh_token(self.refresh_token)

        self.authorization_data = AuthorizationData(
            account_id=self.account_id,
            customer_id=self.customer_id,
            developer_token=self.developer_token,
            authentication=authentication,
        )

        self.reporting_service_manager = ReportingServiceManager(
            authorization_data=self.authorization_data,
            poll_interval_in_milliseconds=5000,
            environment="production",
        )

        logger.info(f"Bing Ads autenticado. Account: {self.account_id}")

    def get_campaign_columns(self) -> List[str]:
        """Colunas padrão para relatório de campanha."""
        return [
            "AccountId",
            "AccountName",
            "CampaignId",
            "CampaignName",
            "CampaignStatus",
            "TimePeriod",
            "Impressions",
            "Clicks",
            "Spend",
            "Conversions",
            "Revenue",
            "CostPerConversion",
            "AverageCpc",
            "Ctr",
            "AveragePosition",
        ]

    def get_ad_performance_columns(self) -> List[str]:
        """Colunas para relatório de performance de anúncios."""
        return [
            "AccountId",
            "AccountName",
            "CampaignId",
            "CampaignName",
            "AdGroupId",
            "AdGroupName",
            "AdId",
            "AdTitle",
            "TimePeriod",
            "Impressions",
            "Clicks",
            "Spend",
            "Conversions",
            "Revenue",
        ]

    @retry(tries=3, delay=60, backoff=2)
    def request_report(self, columns: List[str] = None) -> pd.DataFrame:
        """
        Executa relatório no Bing Ads.
        
        Args:
            columns: Lista de colunas
        
        Returns:
            DataFrame com resultados
        """
        if columns is None:
            if self.report_type == "AdPerformanceReport":
                columns = self.get_ad_performance_columns()
            else:
                columns = self.get_campaign_columns()

        reporting_service = ServiceClient(
            service="ReportingService",
            version=13,
            authorization_data=self.authorization_data,
            environment="production",
        )

        # Cria request do relatório
        report_request = self._build_report_request(reporting_service, columns)

        reporting_download_parameters = ReportingDownloadParameters(
            report_request=report_request,
            result_file_directory="/tmp",
            result_file_name=f"bing_report_{self.account_id}",
            overwrite_result_file=True,
            timeout_in_milliseconds=self.TIMEOUT_IN_MILLISECONDS,
        )

        logger.info(f"Iniciando download do relatório Bing account_id={self.account_id}")

        result_file_path = self.reporting_service_manager.download_file(
            reporting_download_parameters
        )

        if not result_file_path:
            logger.warning("Nenhum dado retornado")
            return pd.DataFrame()

        # Lê CSV do relatório
        df = pd.read_csv(result_file_path, skiprows=10, skipfooter=1, engine="python")

        # Padroniza nomes
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # Adiciona metadados
        df["account_id"] = self.account_id

        # Renomeia data
        if "timeperiod" in df.columns:
            df["date"] = pd.to_datetime(df["timeperiod"]).dt.strftime("%Y-%m-%d")
        elif "time_period" in df.columns:
            df["date"] = pd.to_datetime(df["time_period"]).dt.strftime("%Y-%m-%d")

        logger.success(f"Extraídos {len(df)} registros do Bing Ads")
        return df

    def _build_report_request(self, service, columns: List[str]):
        """Constrói request do relatório."""
        report_request = service.factory.create(f"{self.report_type}Request")
        report_request.Aggregation = self.REPORT_AGGREGATION
        report_request.ExcludeColumnHeaders = False
        report_request.ExcludeReportFooter = True
        report_request.ExcludeReportHeader = True
        report_request.Format = "Csv"
        report_request.ReturnOnlyCompleteData = False

        # Período
        report_time = service.factory.create("ReportTime")
        report_time.CustomDateRangeStart = service.factory.create("Date")
        report_time.CustomDateRangeStart.Year = int(self.start_date[:4])
        report_time.CustomDateRangeStart.Month = int(self.start_date[5:7])
        report_time.CustomDateRangeStart.Day = int(self.start_date[8:10])

        report_time.CustomDateRangeEnd = service.factory.create("Date")
        report_time.CustomDateRangeEnd.Year = int(self.end_date[:4])
        report_time.CustomDateRangeEnd.Month = int(self.end_date[5:7])
        report_time.CustomDateRangeEnd.Day = int(self.end_date[8:10])

        report_request.Time = report_time

        # Scope
        scope = service.factory.create("AccountThroughAdGroupReportScope")
        scope.AccountIds = {"long": [self.account_id]}
        report_request.Scope = scope

        # Colunas
        report_columns = service.factory.create(
            f"ArrayOf{self.report_type.replace('Report', '')}ReportColumn"
        )
        report_columns.CampaignPerformanceReportColumn = columns
        report_request.Columns = report_columns

        return report_request

    def request_report_retry(self, columns: List[str] = None) -> pd.DataFrame:
        """Alias com retry embutido."""
        return self.request_report(columns)
