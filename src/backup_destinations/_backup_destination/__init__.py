import os
import glob

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import NamedTuple

class BackupDestination(ABC):

    def __init__(self, conf_dir: Path, backup_dir: Path, conf: NamedTuple) -> None:
        super().__init__()

        self._conf_dir = conf_dir
        self._backup_dir = backup_dir
        self._conf = conf

        self._timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

    @abstractmethod
    def _upload_file(self, file_path: Path, target_path: str):
        pass

    @abstractmethod
    def _download_file(self, file_name: str, target_path: Path):
        pass

    def upload_backup(self, backup_name: str):
        for file_path in self._backup_dir.glob("*.gpg"):
            target_path = f"{backup_name}/{self._timestamp}/{file_path.name}"
            self._upload_file(file_path, target_path)