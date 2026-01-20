from google.cloud import secretmanager
from loguru import logger


class SecretManager:
    """Class that instantiates Secret Manager client"""

    def __init__(
        self,
    ):
        self.client = secretmanager.SecretManagerServiceClient()

    def update_secret(
        self,
        secret_id: str,
        project_id: str,
        payload,
    ) -> bool:
        """Inserts a new version and destroys the old ones.

        Args:
            secret_id (str): ID of secret
            project_id (str): Project ID where the secret is stored
            payload (any): The value you want to store. If it's a dict

        Returns:
            bool: True if update is successful
        """
        secret_new_version = self.add_secret_version(secret_id, project_id, payload)

        secret_version_to_delete = secret_new_version - 1

        self.destroy_secret_version(secret_id, project_id, secret_version_to_delete)
        return True

    def access_secret_version(
        self, secret_id: str, project_id: str, version_id: str = "latest"
    ) -> str:
        """Access a secret version.

        Args:
            secret_id (str): ID of secret
            project_id (str): Project ID where the secret is stored
            version_id (str, optional): Secret version ID. Defaults to "latest".

        Returns:
            str: Secret contents.
        """
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        logger.info(f"Retrieving secret [{secret_name}]")
        response = self.client.access_secret_version(name=secret_name)

        return response.payload.data.decode("UTF-8")

    def get_latest_version_id(self, secret_id: str, project_id: str) -> int:
        """What's the latest version ID.

        Args:
            secret_id (str): ID of secret
            project_id (str): Project ID where the secret is stored

        Returns:
            int: Version ID
        """
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

        secret_full_version = self.client.get_secret_version(name=secret_name)
        secret_version = secret_full_version.name.split("/")[5]

        return int(secret_version)

    def add_secret_version(self, secret_id: str, project_id: str, payload: any) -> int:
        """Creates a new version with new contents.

        Args:
            secret_id (str): ID of secret
            project_id (str): Project ID where the secret is stored
            payload (any): The value you want to store.

        Returns:
            int: The ID of the newly created version.
        """
        secret_name = f"projects/{project_id}/secrets/{secret_id}"

        secret_payload = secretmanager.SecretPayload(
            data=bytes(payload.encode("UTF-8"))
        )

        secret_add_version_request = secretmanager.AddSecretVersionRequest(
            parent=secret_name, payload=secret_payload
        )

        logger.info(f"Saving new secret version for [{secret_name}]")
        new_version = self.client.add_secret_version(request=secret_add_version_request)
        new_version_number = int(new_version.name.split("/")[5])

        return new_version_number

    def destroy_secret_version(
        self, secret_id: str, project_id: str, version_id: str
    ) -> bool:
        """Destroys a secret version.

        Args:
            secret_id (str): ID of secret
            project_id (str): Project ID where the secret is stored
            version_id (str): Secret version ID.

        Returns:
            bool: Returns true if destroy action is successful.
        """
        secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

        logger.info(f"Destroying secret version [{secret_name}]")
        self.client.destroy_secret_version(request={"name": secret_name})
        return True
