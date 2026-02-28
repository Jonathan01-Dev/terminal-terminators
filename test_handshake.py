import socket
from src.security.handshake import HandshakeManager

def test_secure_conn():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 5050))
        print("📡 Connecté. Lancement du handshake...")
        
        key = HandshakeManager.do_client_handshake(s)
        if key:
            print(f"✅ Handshake RÉUSSI ! Clé AES établie : {key.hex()[:10]}...")
        else:
            print("❌ Échec du handshake.")
    finally:
        s.close()

if __name__ == "__main__":
    test_secure_conn()