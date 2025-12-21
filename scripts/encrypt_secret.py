from cryptography.fernet import Fernet

if __name__ == "__main__":
    key = input("Enter the encryption key: ")
    input_secret = input("Enter the secret to encrypt: ")

    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(input_secret.encode())
    print()
    print("Encrypted secret:")
    print(encrypted_text.decode())