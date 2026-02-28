import socket
import threading
from src.network.protocol import receive_tlv, MSG_TEXT
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

security_mgr = HandshakeManager()

def handle_client(conn, addr):
    print(f"🤝 Handshake avec Alice ({addr})...")
    session_key = security_mgr.do_server_handshake(conn)
    
    if session_key:
        crypto = ArchipelEncryption(session_key)
        print(f"🔒 Tunnel sécurisé établi.")
        
        try:
            m_type, encrypted_value = receive_tlv(conn)
            if m_type == MSG_TEXT:
                # Déchiffrement
                plain_text = crypto.decrypt_data(encrypted_value)
                print(f"✅ Message déchiffré de Bob : {plain_text.decode()}")
        except Exception as e:
            print(f"❌ Erreur de déchiffrement : {e}")
        finally:
            conn.close()

def start_bob_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5050))
    server.listen(5)
    print("👤 Bob (Serveur) attend le message d'Alice...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_bob_server()