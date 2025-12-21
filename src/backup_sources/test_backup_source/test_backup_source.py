import os
import shutil

from pathlib import Path
from typing import NamedTuple

from .._backup_source import BackupSource

class TestBackupSourceConfig(NamedTuple):
    pass

class TestBackupSource(BackupSource):

    def __init__(self, workdir: Path, backup_dir: Path, conf: TestBackupSourceConfig) -> None:
        super().__init__(workdir, backup_dir, conf)
        self.__conf = conf
        self.__files_dir = Path(__file__).parent / "_files"

    def create_backup(self):
        self.__copy_file()

    def __copy_file(self):
        shutil.copy2(Path(self.__files_dir / "backup.json"), Path(self._backup_dir / "backup.json"))

