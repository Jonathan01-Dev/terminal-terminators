import socket
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption
from src.network.protocol import format_tlv, MSG_TEXT

def send_to_bob():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 5050))
        
        # 1. Négocier la clé (Handshake)
        session_key = HandshakeManager.do_client_handshake(s)
        
        if session_key:
            crypto = ArchipelEncryption(session_key)
            message = "Salut Bob, ceci est un secret d'Archipel !"
            
            # 2. CHIFFRER le texte
            encrypted_msg = crypto.encrypt_data(message.encode())
            print(f"📤 Alice envoie (chiffré) : {encrypted_msg.hex()[:20]}...")
            
            # 3. Envoyer via TLV
            s.sendall(format_tlv(MSG_TEXT, encrypted_msg))
            print("🚀 Message envoyé.")
            
    finally:
        s.close()

if __name__ == "__main__":
    send_to_bob()