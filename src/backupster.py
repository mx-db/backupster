import yaml

from pathlib import Path
from typing import NamedTuple

import backup_sources as src
import backup_destinations as dst
import backup_utils as bu

class _BackupsterSrcConf(NamedTuple):
    type: str
    conf: src.DavBackupSourceConfig | src.VaultwardenBackupSourceConfig | src.TestBackupSourceConfig | None

class _BackupsterDstConf(NamedTuple):
    type: str
    conf: dst.GCPBackupDestinationConfig

class _BackupsterConf(NamedTuple):
    src: _BackupsterSrcConf
    dst: _BackupsterDstConf
    gpg: str

class _SopsConf(NamedTuple):
    type: str
    secret_path: str
    conf: bu.SopsConfGCP


class ConfParser:

    @staticmethod
    def parse_sops_conf(data: dict) -> _SopsConf:
        return _SopsConf(
            type=data["type"],
            secret_path=data["secret_path"],
            conf=bu.SopsConfGCP(
                kms_id=data["conf"]["gcp_kms_id"],
                svc_key=data["conf"]["gcp_svc_key"]
            )
        )

    @staticmethod
    def parse_backupster_src_conf(data: dict) -> _BackupsterSrcConf:
        src_type = data["type"]
        if src_type == "dav":
            conf = src.DavBackupSourceConfig(
                caldav_url=data["conf"]["caldav_url"],
                caldav_username=data["conf"]["caldav_username"],
                caldav_password=data["conf"]["caldav_password"],
                carddav_url=data["conf"]["carddav_url"],
                carddav_username=data["conf"]["carddav_username"],
                carddav_password=data["conf"]["carddav_password"]
            )
        elif src_type == "vaultwarden":
            conf = src.VaultwardenBackupSourceConfig(
                url=data["conf"]["vw_url"],
                client_id=data["conf"]["vw_client_id"],
                client_secret=data["conf"]["vw_client_secret"],
                password=data["conf"]["vw_password"]
            )
        elif src_type == "test":
            conf = src.TestBackupSourceConfig()
        else:
            raise ValueError(f"Unknown source type: {src_type}")
        
        return _BackupsterSrcConf(
            type=src_type,
            conf=conf
        )
    
    @staticmethod
    def parse_backupster_dst_conf(data: dict) -> _BackupsterDstConf:
        dst_type = data["type"]
        if dst_type == "gcp":
            conf = dst.GCPBackupDestinationConfig(
                bucket_name=data["conf"]["gcp_bucket_name"],
                svc_key=data["conf"]["gcp_svc_key"]
            )
        else:
            raise ValueError(f"Unknown destination type: {dst_type}")
        
        return _BackupsterDstConf(
            type=dst_type,
            conf=conf
        )
    
    @staticmethod
    def parse_backupster_conf(data: dict) -> _BackupsterConf:
        return _BackupsterConf(
            src=ConfParser.parse_backupster_src_conf(data["src"]),
            dst=ConfParser.parse_backupster_dst_conf(data["dst"]),
            gpg=data["gpg"]
        )


class Backupster:
    def __init__(self):
        self.__work_dir = Path(".workdir")
        self.__conf_dir = Path(self.__work_dir, ".conf")
        self.__backup_dir = Path(".backup")
        self.__mount_dir = Path(".mnt")

        mnt_conf_sops_file = self.__mount_dir / "sops.yaml"
        mnt_conf_backupster_file = self.__mount_dir / "backupster.yaml"

        sops = self.__load_sops(mnt_conf_sops_file)
        conf_raw = sops.decrypt_file(mnt_conf_backupster_file)

        if conf_raw:
            conf = ConfParser.parse_backupster_conf(conf_raw)
            self.__src_type = conf.src.type
            if self.__src_type == "dav" and isinstance(conf.src.conf, src.DavBackupSourceConfig):
                self.source = src.DavBackupSource(self.__work_dir, self.__backup_dir, conf.src.conf)
            elif self.__src_type == "vaultwarden" and isinstance(conf.src.conf, src.VaultwardenBackupSourceConfig):
                self.source = src.VaultwardenBackupSource(self.__work_dir, self.__backup_dir, conf.src.conf)
            elif self.__src_type == "test" and isinstance(conf.src.conf, src.TestBackupSourceConfig):
                self.source = src.TestBackupSource(self.__work_dir, self.__backup_dir, conf.src.conf)
            else:
                raise ValueError(f"Unknown source type: {self.__src_type}")
    
            self.__dst_type = conf.dst.type
            if self.__dst_type == "gcp" and isinstance(conf.dst.conf, dst.GCPBackupDestinationConfig):
                self.destination = dst.GCPBackupDestination(self.__conf_dir, self.__backup_dir, conf.dst.conf)

            self.__gpg = bu.SimpleGPG(conf.gpg)

    def __load_sops(self, conf_file: Path) -> bu.SimpleSops:
        with open(conf_file, "r") as f:
            conf = ConfParser.parse_sops_conf(yaml.safe_load(f))

        sops_type = conf.type
        pw_path = conf.secret_path
        with open(pw_path, "r") as pw_file:
            pw = pw_file.read().strip()

        if sops_type == "gcp" and isinstance(conf.conf, bu.SopsConfGCP):
            return bu.SimpleSops(self.__conf_dir, pw, sops_type, conf.conf)

        raise SopsError("No valid SOPS provider configured!")

    def __get_subdirs(self, dir_path: Path) -> list[Path]:
        return [entry for entry in dir_path.iterdir() if entry.is_dir()]

    def __zip_backup(self):
        for subdir in self.__get_subdirs(self.__backup_dir):
            bu.zip_directory(self.__backup_dir, subdir.name, self.__backup_dir)

    def __encrypt_backup(self):
        for entry in Path(self.__backup_dir).iterdir():
            if entry.is_file() and not entry.name.startswith("."):  # check if it's a file
                self.__gpg.encrypt_file(entry, f"{entry}.gpg")

    def __cleanup(self):
        bu.cleanup_dir(self.__work_dir, exceptions=[self.__conf_dir.name])
        bu.cleanup_dir(self.__backup_dir)


    def backup(self):
        self.source.create_backup()
        self.__zip_backup()
        self.__encrypt_backup()
        self.destination.upload_backup(self.__src_type)
        self.__cleanup()


class SopsError(Exception):
    pass