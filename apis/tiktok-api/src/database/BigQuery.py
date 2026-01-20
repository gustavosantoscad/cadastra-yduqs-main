"""
BigQuery Database Module
Responsável pela conexão e exportação de dados para BigQuery
"""

from typing import Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from loguru import logger
import pandas as pd

class BigQuery:
    """Classe para interação com Google BigQuery"""

    def __init__(
        self,
        project_id: str,
        credentials_path: Optional[str] = None,
    ):
        """
        Inicializa conexão com BigQuery.

        Args:
            project_id: ID do projeto GCP
            credentials_path: Caminho para arquivo de credenciais (opcional)
        """
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.client: Optional[bigquery.Client] = None

    def auth(self) -> None:
        """
        Autentica com BigQuery.
        Usa ADC (Application Default Credentials) no Cloud Run.
        """
        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = bigquery.Client(
                    project=self.project_id,
                    credentials=credentials,
                )
            else:
                # Usa ADC (Application Default Credentials)
                self.client = bigquery.Client(project=self.project_id)

            logger.info(f"BigQuery authenticated for project: {self.project_id}")

        except Exception as e:
            logger.error(f"BigQuery authentication failed: {e}")
            raise

    def _delete_existing_data(
        self,
        destination_table: str,
        start_date: str,
        end_date: str,
        advertiser_id: str,
    ) -> int:
        """
        Remove dados existentes no período para evitar duplicação.

        Args:
            destination_table: Tabela de destino (dataset.table)
            start_date: Data inicial
            end_date: Data final
            advertiser_id: ID do anunciante

        Returns:
            Número de linhas deletadas
        """
        query = f"""
        DELETE FROM `{self.project_id}.{destination_table}`
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        AND _advertiser_id = '{advertiser_id}'
        """

        try:
            if self.client is None:
                raise ValueError("BigQuery client not initialized. Call auth() first.")
            job = self.client.query(query)
            job.result()
            deleted_rows = job.num_dml_affected_rows or 0
            logger.info(
                f"Deleted {deleted_rows} existing rows for period "
                f"{start_date} to {end_date}"
            )
            return deleted_rows

        except Exception as e:
            # Tabela pode não existir ainda
            logger.warning(f"Could not delete existing data: {e}")
            return 0

    def export(
        self,
        df: pd.DataFrame,
        destination_table: str,
        start_date: str,
        end_date: str,
        advertiser_id: str,
        if_exists: str = "append",
    ) -> int:
        """
        Exporta DataFrame para BigQuery.

        Args:
            df: DataFrame com dados
            destination_table: Tabela destino (dataset.table)
            start_date: Data inicial do período
            end_date: Data final do período
            advertiser_id: ID do anunciante
            if_exists: Comportamento se tabela existe (append/replace/fail)

        Returns:
            Número de linhas inseridas
        """
        if df.empty:
            logger.warning("DataFrame is empty. Nothing to export.")
            return 0

        full_table_id = f"{self.project_id}.{destination_table}"

        try:
            # Remove dados existentes no período (evita duplicação)
            if if_exists == "append":
                self._delete_existing_data(
                    destination_table=destination_table,
                    start_date=start_date,
                    end_date=end_date,
                    advertiser_id=advertiser_id,
                )

            # Configura job de carga
            job_config = bigquery.LoadJobConfig(
                write_disposition=(
                    bigquery.WriteDisposition.WRITE_TRUNCATE
                    if if_exists == "replace"
                    else bigquery.WriteDisposition.WRITE_APPEND
                ),
                autodetect=True,
            )

            # Executa carga
            if self.client is None:
                raise ValueError("BigQuery client not initialized. Call auth() first.")
            job = self.client.load_table_from_dataframe(
                df,
                full_table_id,
                job_config=job_config,
            )
            job.result()

            # Verifica resultado
            if self.client is None:
                raise ValueError("BigQuery client not initialized. Call auth() first.")
            table = self.client.get_table(full_table_id)
            logger.info(
                f"Exported {len(df)} rows to {full_table_id}. "
                f"Total rows in table: {table.num_rows}"
            )

            return len(df)

        except Exception as e:
            logger.error(f"BigQuery export failed: {e}")
            raise

    def table_exists(self, destination_table: str) -> bool:
        """
        Verifica se tabela existe.

        Args:
            destination_table: Nome da tabela (dataset.table)

        Returns:
            True se existe, False caso contrário
        """
        full_table_id = f"{self.project_id}.{destination_table}"

        try:
            if self.client is None:
                raise ValueError("BigQuery client not initialized. Call auth() first.")
            self.client.get_table(full_table_id)
            return True
        except Exception:
            return False

    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Executa query e retorna resultado como DataFrame.

        Args:
            query: Query SQL

        Returns:
            DataFrame com resultado
        """
        try:
            if self.client is None:
                raise ValueError("BigQuery client not initialized. Call auth() first.")
            job = self.client.query(query)
            return job.to_dataframe()
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise
