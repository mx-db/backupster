import gnupg
import base64

class SimpleGPG:
    def __init__(self, public_key_base64: str):
        self.__gpg = gnupg.GPG()
        self.__fingerprint = self.__import_key(public_key_base64)

    def __import_key(self, public_key_base64: str) -> str:
        key_import = self.__gpg.import_keys(base64.b64decode(public_key_base64))
        self.__gpg.trust_keys(key_import.fingerprints, 'TRUST_ULTIMATE')
        return key_import.fingerprints[0]

    def encrypt_file(self, file_path, output_path):
        with open(file_path, 'rb') as file:
            status = self.__gpg.encrypt_file(file, recipients=[self.__fingerprint], output=output_path)

            if not status.ok:
                raise MyGPGEncryptionError("Failed to encrypt file:\n" + status.stderr)


class MyGPGEncryptionError(Exception):
    pass