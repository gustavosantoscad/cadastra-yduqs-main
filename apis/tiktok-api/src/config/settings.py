"""
Configurações do projeto TikTok Ads API
"""

# GCP Settings
PROJECT_ID = "cadastra-yducs-prod"
DATASET_ID = "RAW"

# Tabelas de destino no BigQuery
# Padrão: TKT + Numeração + Nome descritivo (CAPS LOCK)
TABLES = {
    "advertiser": "TKT001_TIKTOK_ADS_ADVERTISER",
    "campaign": "TKT002_TIKTOK_ADS_CAMPAIGN",
    "adgroup": "TKT003_TIKTOK_ADS_ADGROUP",
    "ad": "TKT004_TIKTOK_ADS_AD",
}

# TikTok API Settings
TIKTOK_API_BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"
TIKTOK_REPORT_ENDPOINT = "/report/integrated/get/"

# Dimensões por nível de relatório
DIMENSIONS = {
    "advertiser": ["advertiser_id", "stat_time_day"],
    "campaign": ["campaign_id", "stat_time_day"],
    "adgroup": ["adgroup_id", "stat_time_day"],
    "ad": ["ad_id", "stat_time_day"],
}

# Data levels correspondentes
DATA_LEVELS = {
    "advertiser": "AUCTION_ADVERTISER",
    "campaign": "AUCTION_CAMPAIGN",
    "adgroup": "AUCTION_ADGROUP",
    "ad": "AUCTION_AD",
}

# Métricas disponíveis (todas)
METRICS = [
    # Basic / Core
    "spend",
    "impressions",
    "clicks",
    "ctr",
    "cpc",
    "cpm",
    "reach",
    "frequency",
    
    # Engagement / Social
    "profile_visits",
    "likes",
    "comments",
    "shares",
    "follows",
    "engagements",
    "clicks_on_music_disc",
    
    # Video
    "video_play_actions",
    "video_watched_2s",
    "video_watched_6s",
    "average_video_play",
    "average_video_play_per_user",
    "video_views_p25",
    "video_views_p50",
    "video_views_p75",
    "video_views_p100",
    
    # Conversion
    "conversions",
    "conversion_rate",
    "cost_per_conversion",
    "real_time_conversions",
    "real_time_conversion_rate",
    "cost_per_real_time_conversion",
    "results",
    "result_rate",
    "cost_per_result",
    "real_time_result",
    "real_time_result_rate",
    "real_time_cost_per_result",
    
    # In-App Events
    "app_install",
    "real_time_app_install",
    "registration",
    "total_registration",
    "purchase",
    "total_purchase",
    "total_purchase_value",
    "app_event_add_to_cart",
    "total_app_event_add_to_cart",
    "total_app_event_add_to_cart_value",
    "checkout",
    "total_checkout",
    "total_checkout_value",
    "view_content",
    "total_view_content",
    "total_view_content_value",
    "add_payment_info",
    "total_add_payment_info",
    "add_to_wishlist",
    "total_add_to_wishlist",
    "total_add_to_wishlist_value",
    "complete_tutorial",
    "total_complete_tutorial",
    "login",
    "total_login",
    "search",
    "total_search",
    "subscribe",
    "total_subscribe",
    "total_subscribe_value",
    
    # Attribution
    "vta_conversion",
    "vta_purchase",
    "cta_conversion",
    "cta_purchase",
    
    # Cost metrics
    "cost_per_1000_reached",
    "cost_per_app_install",
    "cost_per_registration",
    "cost_per_purchase",
]

# Dias de reprocessamento padrão
DEFAULT_DAYS_REPROCESS = 3
