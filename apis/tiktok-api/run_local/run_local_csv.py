"""
Script para teste local da API TikTok Ads.
Exporta os dados para arquivos CSV ao invés de BigQuery.

Uso:
    1. Preencha as credenciais abaixo
    2. Execute: python run_local_csv.py
    3. Os arquivos CSV serão gerados na pasta 'output/'
"""

import os
import sys, requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ADVERTISER_IDS = os.getenv("ADVERTISER_IDS")
START_DATE = os.getenv("START_DATE")
END_DATE = os.getenv("END_DATE")
REPORT_TYPES = os.getenv("REPORT_TYPES")


# Set console encoding to UTF-8 for Windows to display emojis correctly
if sys.platform == "win32":
    os.system("chcp 65001 > nul")

# Adiciona o diretório src ao path para importar os módulos
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
from loguru import logger
from config.settings import TABLES, DIMENSIONS, DATA_LEVELS
from controller.TikTokAdsController import TikTokAdsController


# ============================================================
# 📝 PREENCHA SUAS CREDENCIAIS AQUI
# ============================================================

CONFIG = {
    # Token de acesso do TikTok Business API
    "access_token": ACCESS_TOKEN,
    
    # Lista de Advertiser IDs para extrair
    "advertiser_ids": [
        "ADVERTISER_IDS",  # Substitua pelo seu advertiser_id
    ],
    
    # Período de extração (deixe vazio para usar os últimos 3 dias)
    "start_date": "",  # Formato: "2025-01-01"
    "end_date": "",    # Formato: "2025-01-15"
    
    # Tipos de relatório a extrair (comente os que não quiser)
    "report_types": [
        "advertiser",
        "campaign",
        "adgroup",
        "ad",
    ],
    
    # Pasta de saída para os CSVs
    "output_dir": "output",
}

# ============================================================


def setup_logging():
    """Configura logging."""
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
        level="INFO",

    )


def get_date_range() -> tuple[str, str]:
    """Calcula período de datas."""
    start_date = CONFIG.get("start_date", "")
    end_date = CONFIG.get("end_date", "")
    
    if not start_date or not end_date:
        end_date_dt = datetime.utcnow() - timedelta(days=1)
        start_date_dt = end_date_dt - timedelta(days=2)
        start_date = start_date_dt.strftime("%Y-%m-%d")
        end_date = end_date_dt.strftime("%Y-%m-%d")
    
    return start_date, end_date


def create_output_dir():
    """Cria diretório de saída."""
    output_dir = Path(CONFIG["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def run_extraction():
    """Executa extração e salva em CSV."""
    setup_logging()
    
    logger.info("=" * 60)
    logger.info("🚀 Iniciando extração TikTok Ads (Modo Local - CSV)")
    logger.info("=" * 60)
    
    # Valida configurações
    if CONFIG["access_token"] == ACCESS_TOKEN:
        logger.error("❌ Preencha o access_token no arquivo!")
        logger.info("Abra run_local_csv.py e configure suas credenciais.")
        return
    
    if CONFIG["advertiser_ids"][0] == ADVERTISER_IDS:
        logger.error("❌ Preencha o advertiser_id no arquivo!")
        logger.info("Abra run_local_csv.py e configure suas credenciais.")
        return
    
    # Prepara
    start_date, end_date = get_date_range()
    output_dir = create_output_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    logger.info(f"📅 Período: {start_date} a {end_date}")
    logger.info(f"📁 Pasta de saída: {output_dir.absolute()}")
    logger.info(f"👥 Advertisers: {CONFIG['advertiser_ids']}")
    logger.info(f"📊 Relatórios: {CONFIG['report_types']}")
    logger.info("-" * 60)
    
    results_summary = []
    
    for advertiser_id in CONFIG["advertiser_ids"]:
        advertiser_id = str(advertiser_id).replace("-", "").strip()
        logger.info(f"\n🏢 Processando Advertiser: {advertiser_id}")
        
        for report_type in CONFIG["report_types"]:
            if report_type not in TABLES:
                logger.warning(f"⚠️ Tipo '{report_type}' não suportado")
                continue
            
            table_name = TABLES[report_type]
            logger.info(f"  📈 Extraindo: {report_type.upper()}")
            
            try:
                # Inicializa controller
                controller = TikTokAdsController(
                    access_token=CONFIG["access_token"],
                    advertiser_id=advertiser_id,
                    start_date=start_date,
                    end_date=end_date,
                    report_type=report_type,
                )
                
                # Extrai dados
                df = controller.fetch_report_retry()
                
                if df.empty:
                    logger.warning(f"  ⚠️ Sem dados para {report_type}")
                    results_summary.append({
                        "advertiser_id": advertiser_id,
                        "report_type": report_type,
                        "rows": 0,
                        "status": "empty",
                        "file": None,
                    })
                    continue
                
                # Salva CSV
                filename = f"{table_name}_{advertiser_id}_{timestamp}.csv"
                filepath = output_dir / filename
                
                df.to_csv(filepath, index=False, encoding="utf-8-sig")
                
                logger.info(f"  ✅ Salvo: {filename} ({len(df)} linhas)")
                
                results_summary.append({
                    "advertiser_id": advertiser_id,
                    "report_type": report_type,
                    "rows": len(df),
                    "status": "success",
                    "file": str(filepath),
                })
                
            except Exception as e:
                logger.error(f"  ❌ Erro em {report_type}: {e}")
                results_summary.append({
                    "advertiser_id": advertiser_id,
                    "report_type": report_type,
                    "rows": 0,
                    "status": "error",
                    "file": None,
                    "error": str(e),
                })
    
    # Resumo final
    logger.info("\n" + "=" * 60)
    logger.info("📋 RESUMO DA EXTRAÇÃO")
    logger.info("=" * 60)
    
    total_rows = 0
    successful = 0
    
    for r in results_summary:
        status_icon = "✅" if r["status"] == "success" else "⚠️" if r["status"] == "empty" else "❌"
        logger.info(f"{status_icon} {r['report_type'].upper():12} | {r['rows']:>6} linhas | {r['status']}")
        total_rows += r["rows"]
        if r["status"] == "success":
            successful += 1
    
    logger.info("-" * 60)
    logger.info(f"📊 Total: {total_rows} linhas em {successful} arquivos")
    logger.info(f"📁 Arquivos salvos em: {output_dir.absolute()}")
    logger.info("=" * 60)
    
    # Lista arquivos gerados
    csv_files = list(output_dir.glob("*.csv"))
    if csv_files:
        logger.info("\n📄 Arquivos gerados:")
        for f in sorted(csv_files):
            size_kb = f.stat().st_size / 1024
            logger.info(f"   • {f.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    run_extraction()
