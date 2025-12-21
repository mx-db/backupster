import os
import base64

from typing import NamedTuple
from pathlib import Path

from google.cloud import storage

from .._backup_destination import BackupDestination

class GCPBackupDestinationConfig(NamedTuple):
    svc_key: str
    bucket_name: str

class GCPBackupDestination(BackupDestination):

    def __init__(self, conf_dir: Path, backup_dir: Path, conf: GCPBackupDestinationConfig) -> None:
        super().__init__(conf_dir, backup_dir, conf)

        self.__bucket_name = conf.bucket_name
        self.__svc_path = Path(self._conf_dir, ".gcp_svc.json")

        self.__setup_auth(conf.svc_key)

    def __setup_auth(self, svc_key_b64: str):
        with open(self.__svc_path, "w") as f:
            svc_key = base64.b64decode(svc_key_b64).decode()
            f.write(svc_key)
            os.chmod(self.__svc_path, 0o400)

    def __setup_env(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(self.__svc_path)

    def _upload_file(self, file_path: Path, target_path: str):
        self.__upload_blob(file_path, target_path)

    def _download_file(self, file_name: str, target_path: Path):
        return self.__download_blob(file_name, target_path)
    

    #### Helpers ####


    def __upload_blob(self, source_file: Path, destination_blob_name: str):
        self.__setup_env()

        storage_client = storage.Client()
        bucket = storage_client.bucket(self.__bucket_name)
        blob = bucket.blob(destination_blob_name)

        blob.upload_from_filename(source_file)

        print(f"File {source_file.name} uploaded to {destination_blob_name}.")

    def __download_blob(self, source_blob_name: str, destination_file: Path):
        self.__setup_env()

        storage_client = storage.Client()
        bucket = storage_client.bucket(self.__bucket_name)
        blob = bucket.blob(source_blob_name)

        blob.download_to_filename(destination_file)

        print(f"Blob {source_blob_name} downloaded to {destination_file.name}.")