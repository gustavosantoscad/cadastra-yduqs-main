import json
from cadastra_core import SecretManager
from loguru import logger
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def google_main(request):
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

        current_value_json = json.loads(current_value)

        creds = Credentials.from_authorized_user_info(current_value_json)

        if creds and creds.refresh_token:
            if force_refresh or creds.expired:
                logger.info(f"Refreshing tokens [{project_id}/{secret_id}]")
                creds.refresh(Request())
                new_value_json = json.loads(creds.to_json())

                for key in current_value_json.keys():
                    if key not in new_value_json.keys():
                        new_value_json[key] = current_value_json[key]

                logger.info(f"Updating tokens [{project_id}/{secret_id}]")
                secret_manager_client.update_secret(
                    secret_id, project_id, json.dumps(new_value_json)
                )
                logger.success(f"Successfully updated [{project_id}/{secret_id}]")
                return ({"success": True}, 200)

        logger.success(f"No need to update [{project_id}/{secret_id}]")
        return ({"success": True}, 200)

    except Exception as e:
        if "invalid_grant" in e.__str__():
            logger.error("Invalid token, you'll need to generate a new one")
        logger.error(e)
        return ({"success": False}, 500)
