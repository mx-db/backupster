from cryptography.fernet import Fernet

def decrypt_string(pw: str, encrypted: str) -> str:
    cipher_suite = Fernet(pw)
    decoded_text = cipher_suite.decrypt(encrypted)
    return decoded_text.decode()

def encrypt_string(pw: bytes | str, plain: str) -> str:
    cipher_suite = Fernet(pw)
    encoded_text = cipher_suite.encrypt(plain.encode())
    return encoded_text.decode()