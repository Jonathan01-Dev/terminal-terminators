import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class ArchipelEncryption:
    def __init__(self, session_key):
        self.aesgcm = AESGCM(session_key)

    def encrypt_data(self, data_bytes):
        """Chiffre les données et ajoute un Nonce (IV) unique de 12 octets"""
        nonce = os.urandom(12)
        # On chiffre sans données associées additionnelles (None)
        ciphertext = self.aesgcm.encrypt(nonce, data_bytes, None)
        return nonce + ciphertext

    def decrypt_data(self, encrypted_bytes):
        """Sépare le nonce des données et déchiffre"""
        nonce = encrypted_bytes[:12]
        ciphertext = encrypted_bytes[12:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)