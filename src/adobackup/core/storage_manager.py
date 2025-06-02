from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import AzureError
from configparser import ConfigParser
import logging
import os
import json

class StorageManager:
    """Manages Azure Blob Storage operations for backups"""

    def __init__(self, connection_string=None):
        self.logger = logging.getLogger(__name__)
        self.connection_string = (
            connection_string or 
            os.getenv('AZURE_STORAGE_CONNECTION_STRING') or
            self._load_from_config()
        )

        if not self.connection_string:
            raise ValueError("Azure Storage connection string not configured")

        self.client = BlobServiceClient.from_connection_string(self.connection_string)

    def _load_from_config(self):
        """Load connection string from config/settings.ini"""
        try:
            config = ConfigParser()
            config.read('config/settings.ini')
            return config.get('azure', 'storage_connection_string')
        except Exception as e:
            self.logger.warning(f"Failed to load config: {str(e)}")
            return None

    def upload_file_to_blob(self, file_path: str, blob_name: str = "latest_backup.json", container_name: str = "backups"):
        """Uploads a file to Azure Blob Storage"""
        try:
            container_client = self.client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()

            with open(file_path, "rb") as f:
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.upload_blob(f, overwrite=True)

            self.logger.info(f"Uploaded file to blob {blob_name} in container {container_name}")
            return True

        except AzureError as e:
            self.logger.error(f"Upload failed: {str(e)}")
            raise

    def upload_backup(self, container_name: str, blob_name: str, data: str):
        """(Legacy-compatible) Upload raw string backup data"""
        try:
            container_client = self.client.get_container_client(container_name)
            if not container_client.exists():
                container_client.create_container()

            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(data, overwrite=True)
            self.logger.info(f"Uploaded backup to {blob_name}")
            return True

        except AzureError as e:
            self.logger.error(f"Upload failed: {str(e)}")
            raise

    def download_backup(self, blob_path: str):
        """Download blob content as string"""
        try:
            container_name, blob_name = blob_path.split('/', 1)
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            return blob_client.download_blob().readall()

        except AzureError as e:
            self.logger.error(f"Download failed: {str(e)}")
            raise

    def download_to_file(self, blob_name: str = "latest_backup.json", container_name: str = "backups", download_path: str = "backups/latest_backup.json"):
        """Download blob and write it to a local file"""
        try:
            blob_client = self.client.get_blob_client(container=container_name, blob=blob_name)
            stream = blob_client.download_blob()
            os.makedirs(os.path.dirname(download_path), exist_ok=True)
            with open(download_path, "wb") as f:
                f.write(stream.readall())
            self.logger.info(f"Downloaded blob to local path: {download_path}")
            return download_path

        except AzureError as e:
            self.logger.error(f"Download to file failed: {str(e)}")
            raise

    def save_locally(self, results: dict, path: str = "backups/latest_backup.json"):
        """Save dict as a JSON file locally"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        self.logger.info(f"Saved local backup to {path}")
