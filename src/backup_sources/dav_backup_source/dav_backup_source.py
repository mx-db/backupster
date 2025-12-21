import os
import subprocess

from string import Template
from typing import NamedTuple
from pathlib import Path

from .._backup_source import BackupSource

class DavBackupSourceConfig(NamedTuple):
    carddav_url: str
    carddav_username: str
    carddav_password: str
    caldav_url: str
    caldav_username: str
    caldav_password: str

class DavBackupSource(BackupSource):

    def __init__(self, work_dir: Path, backup_dir: Path, conf: DavBackupSourceConfig) -> None:
        super().__init__(work_dir, backup_dir, conf)
        self.__conf = conf
        self.__files_dir = Path(__file__).parent / "_files"

    def create_backup(self):
        self.__create_config()
        self.__backup()

    
    #### Helpers ####


    def __create_config(self):
        d = {
            'VDIR_PATH': self._work_dir,
            'BAK_PATH': self._backup_dir,
            'CARDDAV_URL': self.__conf.carddav_url,
            'CARDDAV_USERNAME': self.__conf.carddav_username,
            'CARDDAV_PASSWORD': self.__conf.carddav_password,
            'CALDAV_URL': self.__conf.caldav_url,
            'CALDAV_USERNAME': self.__conf.caldav_username,
            'CALDAV_PASSWORD': self.__conf.caldav_password
        }

        with open(self.__files_dir / "config.ini.tpl", 'r') as f:
            vconfig_tpl = Template(f.read())
            vconfig = vconfig_tpl.substitute(d)

        with open(self._work_dir / "config.ini", "w") as f:
            f.write(vconfig)
            os.chmod(f"{self._work_dir}/config.ini", 0o400)

    def __backup(self):
        # Discover
        yes_proc = subprocess.Popen(["yes"], stdout=subprocess.PIPE)

        vdir_env = os.environ | {
            "VDIRSYNCER_CONFIG": f"{self._work_dir}/config.ini"
        }

        try:
            subprocess.run(
                ["vdirsyncer", "discover"],
                env=vdir_env,
                stdin=yes_proc.stdout,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
        finally:
            if yes_proc.stdout:
                yes_proc.stdout.close()
            yes_proc.wait()

        # Sync
        subprocess.run(
            ["vdirsyncer", "sync"],
            env=vdir_env,
            check=True,
        )
