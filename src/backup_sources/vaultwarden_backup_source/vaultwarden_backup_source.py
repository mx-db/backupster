import subprocess
import os
import re
import json
import pykeepass

from pathlib import Path
from typing import NamedTuple

from .._backup_source import BackupSource

class VaultwardenBackupSourceConfig(NamedTuple):
    url: str
    client_id: str
    client_secret: str
    password: str

class VaultwardenBackupSource(BackupSource):
    def __init__(self, workdir: Path, backup_dir: Path, conf: VaultwardenBackupSourceConfig) -> None:
        super().__init__(workdir, backup_dir, conf)
        self.__bw_path = "bw"
        self.__conf = conf
        self.__env_login = {**os.environ, **{
            "BW_CLIENTID": self.__conf.client_id,
            "BW_CLIENTSECRET": self.__conf.client_secret,
        }}
        self.__env_unlock = {**os.environ, **{
            "BWPW": self.__conf.password,
        }}

        self.__configure_cli()
        self.__session = self.__create_session()

    def create_backup(self):
        try:
            folders = self.__get_folders()
            items = self.__get_items()

            self.__create_keepass(folders, items)
            self.__create_zip_export()
        finally:
            print(subprocess.run([self.__bw_path, "lock"]))
            print(subprocess.run([self.__bw_path, "logout"]))

    def __configure_cli(self):
        config_res = subprocess.run([self.__bw_path, "config", "server", self.__conf.url], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if config_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error configuring vaultwarden cli: {config_res.stderr.decode()}")
        print(config_res.stdout.decode())

        login_res = subprocess.run([self.__bw_path, "login", "--apikey"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.__env_login)
        if login_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error logging into vaultwarden cli: {login_res.stderr.decode()}")
        print(login_res.stdout.decode())

    def __create_session(self) -> str:
        session_res = subprocess.run([self.__bw_path, "unlock", "--passwordenv", "BWPW"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=self.__env_unlock)
        if session_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error unlocking vaultwarden: {session_res.stderr.decode()}")

        session = re.findall(r'BW_SESSION="(.*)"', session_res.stdout.decode())[0]
        return session

    def __create_zip_export(self):
        export_res = subprocess.run([self.__bw_path, "export", "--format", "zip", "--output", f"{self._backup_dir}/", "--session", self.__session], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if export_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error exporting vaultwarden data: {export_res.stderr.decode()}")

    def __get_folders(self) -> dict[str, str]:
        folder_res = subprocess.run([self.__bw_path, "list", "folders", "--session", self.__session], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if folder_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error retrieving vaultwarden folders: {folder_res.stderr.decode()}")
        
        folders = json.loads(folder_res.stdout)
        folders_map: dict[str, str] = { folder["id"]: folder["name"] for folder in folders }

        return folders_map
    
    def __get_items(self) -> list[dict]:
        item_res = subprocess.run([self.__bw_path, "list", "items", "--session", self.__session], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if item_res.returncode != 0:
            raise VaultwardenBackupSourceError(f"Error retrieving vaultwarden items: {item_res.stderr.decode()}")

        items = json.loads(item_res.stdout)
        return items

    def __create_keepass(self, folders: dict[str, str], items: list[dict]):
        keepass_path = f"{self._backup_dir}/vaultwarden-backup.kdbx"
        keepass_db = pykeepass.create_database(keepass_path, self.__env_unlock["BWPW"])

        # Create groups
        for folder in folders.values():
            groups = folder.split("/")
            last_group: pykeepass.Group = keepass_db.root_group
            for group in groups:
                group_exists: pykeepass.Group | None = keepass_db.find_groups(path=[*last_group.path, group])
                if group_exists:
                    last_group = group_exists
                else:
                    last_group = keepass_db.add_group(last_group, group)

        # Add entries
        for entry in items:
            group_name = folders[entry["folderId"]]
            group = keepass_db.find_groups(path=group_name.split("/"))
            keepass_db.add_entry(group, entry["name"], entry["login"]["username"] if entry["login"]["username"] else "", entry["login"]["password"])

        keepass_db.save()

class VaultwardenBackupSourceError(Exception):
    pass