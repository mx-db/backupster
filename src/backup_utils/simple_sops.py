import os
import base64

from pathlib import Path
from cryptography.fernet import Fernet
from typing import NamedTuple
from abc import ABC, abstractmethod

from sopsy import Sops


class SopsConfGCP(NamedTuple):
    kms_id: str
    svc_key: str

class SopsConfAWS(NamedTuple):
    kms_arn: str
    profile: str = ""
    role: str = ""

class _ConfParser(ABC):
    def _decrypt_string(self, pw: str, encrypted: str) -> str:
        cipher_suite = Fernet(pw)
        decoded_text = cipher_suite.decrypt(encrypted)
        return decoded_text.decode()
    
    @abstractmethod
    def parse_conf(self, pw: str) -> dict:
        pass

class _ConfParserGCP(_ConfParser):
    def __init__(self, conf_dir: Path, conf: SopsConfGCP) -> None:
        super().__init__()
        self.__conf = conf

    def parse_conf(self, pw: str) -> dict:
        svc_key_path = Path.home() / ".config/gcloud/application_default_credentials.json"

        svc_key_b64 = self._decrypt_string(pw, self.__conf.svc_key)
        svc_key = base64.b64decode(svc_key_b64).decode()

        svc_key_path.parent.mkdir(exist_ok=True, parents=True)
        with open(svc_key_path, "w+") as f:
            f.write(svc_key)
            os.chmod(svc_key_path, 0o400)

        conf = {
            "gcp_kms": self.__conf.kms_id
        }

        return conf
    
class __ConfParserAWS(_ConfParser):
    def __init__(self, conf_dir: Path, conf: SopsConfAWS) -> None:
        super().__init__()
        self.__conf_dir = conf_dir
        self.__conf = conf
        
    def parse_conf(self, pw: str) -> dict:
        return super().parse_conf(pw)

class SimpleSops:

    def __init__(self, conf_dir: Path, pw: str, provider: str, config: SopsConfGCP | SopsConfAWS) -> None:
        self.__conf_dir = conf_dir

        if provider == "gcp" and isinstance(config, SopsConfGCP):
            conf_parser = _ConfParserGCP(conf_dir, config)
        elif provider == "aws" and isinstance(config, SopsConfAWS):
            conf_parser = __ConfParserAWS(conf_dir, config)
        else:
            raise SopsError(f"Unknown provider or wrong provider config: {provider}")

        conf = conf_parser.parse_conf(pw)

        self.__config = {
            "creation_rules": [
                conf
            ]
        }

    def decrypt_file(self, src_path: Path, dst_path: Path | None = None) -> dict | None:
        sops = Sops(
            file=Path(src_path),
            config=f"{self.__conf_dir}/.sops.yaml",
            config_dict=self.__config,
            output=dst_path
        )

        if dst_path:
            sops.decrypt()
        else:
            decrypted = sops.decrypt(to_dict=True)
            if isinstance(decrypted, dict):
                return decrypted
            else:
                raise SopsError("Result is no dict!")


class SopsError(Exception):
    pass