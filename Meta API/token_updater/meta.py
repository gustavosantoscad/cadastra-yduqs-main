import json
from cadastra_core import SecretManager
from loguru import logger
import requests

# Verificar versão mais atual da API e informar todos que utilizam o secret em questão: https://developers.facebook.com/docs/marketing-api/insights/
GRAPH_API_VERSION = "v23.0"


def update_meta_token(access_token: str, app_secret: str, app_id: str) -> str:
    """Sends Meta the current token to receive and return a new one.

    Args:
        access_token (str): Access token to be used to generate a new one
        app_secret (str): Secret of the app being used
        app_id (str): ID of the app being used

    Returns:
        str: The new access token
    """
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/oauth/access_token"

    params = {
        "client_id": app_id,
        #"client_secret": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": access_token,
        "set_token_expires_in_60_days": "true",
        "grant_type": "fb_exchange_token",
    }

    response = requests.get(url, params=params)
    response_code = response.status_code
    response_json = response.json()
    print(response_json)
    if response_code == 200:
        return response_json["access_token"]


def meta_main(request):
    try:
        # Read request JSON
        request_json: dict = request.get_json()

        secret_id: str = request_json.get("secret_id")
        project_id: str = request_json.get("project_id")
        force_refresh: str = bool(request_json.get("force_refresh")) or False

        secret_manager_client = SecretManager()

        logger.info(f"Starting update process for [{project_id}/{secret_id}]")
        current_value: str = secret_manager_client.access_secret_version(
            secret_id, project_id
        )

        token_json = json.loads(current_value)

        app_secret = token_json["app_secret"]
        access_token = token_json["access_token"]
        app_id = token_json["app_id"]

        if force_refresh:
            logger.info(f"Refreshing tokens [{project_id}/{secret_id}]")
            new_access_token = update_meta_token(access_token, app_secret, app_id)
            new_value = json.dumps(
                {
                    "app_id": app_id,
                    "app_secret": app_secret,
                    "access_token": new_access_token,
                }
            )

            logger.info(f"Updating tokens [{project_id}/{secret_id}]")
            secret_manager_client.update_secret(secret_id, project_id, new_value)
            logger.success(f"Successfully updated [{project_id}/{secret_id}]")
            return ({"success": True}, 200)

        return ({"success": True}, 200)

    except Exception as e:
        if "invalid_grant" in e.__str__():
            logger.error("Invalid token, you'll need to generate a new one")
        logger.error(e)
        return ({"success": False}, 500)
