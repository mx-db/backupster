from abc import ABC, abstractmethod
from pathlib import Path
from typing import NamedTuple

class BackupSource(ABC):

    def __init__(self, work_dir: Path, backup_dir: Path, conf: NamedTuple) -> None:
        super().__init__()
        self._work_dir = work_dir
        self._backup_dir = backup_dir

    @abstractmethod
    def create_backup(self):
        pass