import socket
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption
from src.network.protocol import format_tlv, MSG_CHAT_TEXT

def send_secure_msg(target_ip, target_port, text):
    """Fonction appelée par main.py pour envoyer un message chiffré"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((target_ip, int(target_port)))
        
        # Handshake RSA/AES
        key = HandshakeManager().do_client_handshake(s)
        if not key:
            return "❌ Échec du Handshake"

        crypto = ArchipelEncryption(key)
        encrypted_data = crypto.encrypt_data(text.encode('utf-8'))
        
        # Envoi TLV
        s.sendall(format_tlv(MSG_CHAT_TEXT, encrypted_data))
        s.close()
        return f"✅ Message chiffré envoyé à {target_ip}"
    
    except Exception as e:
        return f"💥 Erreur : {e}"

# Ajoute aussi celle-ci pour éviter la prochaine erreur sur 'send'
def send_file_secure(target_ip, target_port, file_path):
    # Logique simplifiée pour le test
    return "🚀 Envoi de fichier en cours (logique à compléter)..."