import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from src.network.protocol import (
    format_tlv, receive_tlv, 
    MSG_HELLO, MSG_PUB_KEY, MSG_SESSION_KEY, MSG_HANDSHAKE_READY
)

class HandshakeManager:
    def __init__(self):
        # Génération d'une paire de clés RSA 2048 bits pour le serveur
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_key = self.private_key.public_key()

    def get_public_key_pem(self):
        """Export de la clé publique pour l'envoi au client"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def do_server_handshake(self, conn):
        """Logique côté Serveur : Reçoit HELLO, envoie PubKey, reçoit AES chiffré"""
        try:
            # 1. Attendre HELLO
            m_type, _ = receive_tlv(conn)
            if m_type != MSG_HELLO: return None
            
            # 2. Envoyer la Clé Publique RSA
            conn.sendall(format_tlv(MSG_PUB_KEY, self.get_public_key_pem()))
            
            # 3. Recevoir la clé de session AES chiffrée
            m_type, encrypted_key = receive_tlv(conn)
            if m_type != MSG_SESSION_KEY: return None
            
            # Déchiffrement de la clé AES avec la clé privée RSA
            session_key = self.private_key.decrypt(
                encrypted_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            
            # 4. Confirmer que tout est OK
            conn.sendall(format_tlv(MSG_HANDSHAKE_READY, b"READY"))
            return session_key
        except Exception as e:
            print(f"❌ Erreur Handshake Serveur: {e}")
            return None

    @staticmethod
    def do_client_handshake(conn):
        """Logique côté Client : Envoie HELLO, reçoit PubKey, génère et envoie AES"""
        try:
            # 1. Envoyer HELLO
            conn.sendall(format_tlv(MSG_HELLO, b"HELLO"))
            
            # 2. Recevoir la Clé Publique du serveur
            m_type, pub_key_bytes = receive_tlv(conn)
            if m_type != MSG_PUB_KEY: return None
            server_pub_key = serialization.load_pem_public_key(pub_key_bytes)
            
            # 3. Générer une clé AES-256 (32 octets)
            session_key = os.urandom(32)
            
            # Chiffrer cette clé AES avec la clé publique RSA du serveur
            encrypted_session_key = server_pub_key.encrypt(
                session_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            conn.sendall(format_tlv(MSG_SESSION_KEY, encrypted_session_key))
            
            # 4. Attendre la confirmation READY
            m_type, _ = receive_tlv(conn)
            return session_key if m_type == MSG_HANDSHAKE_READY else None
        except Exception as e:
            print(f"❌ Erreur Handshake Client: {e}")
            return None