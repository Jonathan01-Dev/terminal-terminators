import socket
import time
import sys
import os
from src.network.protocol import receive_tlv, format_tlv, MSG_REQUEST_CHUNK, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

PEERS = [('127.0.0.1', 5060), ('127.0.0.1', 5061)]

def download_with_fallback(filename, total_chunks):
    chunks_received = 0
    current_peer_idx = 0
    os.makedirs("downloads", exist_ok=True)
    
    while chunks_received < total_chunks:
        target = PEERS[current_peer_idx]
        print(f"\n📡 [CLIENT] Connexion à {target}...")
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            s.connect(target)
            
            print("🤝 [CLIENT] Démarrage du Handshake...")
            key = HandshakeManager.do_client_handshake(s)
            
            if not key:
                print("❌ [CLIENT] Clé de session non reçue.")
                raise Exception("Handshake Failed")

            crypto = ArchipelEncryption(key)
            print("🔒 [CLIENT] Session sécurisée établie.")

            while chunks_received < total_chunks:
                # On utilise le nom du fichier pour le test simple
                req = f"{filename}:{chunks_received}".encode()
                s.sendall(format_tlv(MSG_REQUEST_CHUNK, crypto.encrypt_data(req)))
                
                m_type, enc_data = receive_tlv(s)
                if m_type == MSG_FILE_CHUNK:
                    data = crypto.decrypt_data(enc_data)
                    with open(f"downloads/{filename}", "ab") as f:
                        f.write(data)
                    chunks_received += 1
                    print(f"🧩 Bloc {chunks_received}/{total_chunks} récupéré.", end="\r")
                    time.sleep(0.5) # Pour te laisser le temps de couper le serveur !
                else:
                    break
            s.close()

        except Exception as e:
            print(f"\n⚠️ [ERREUR] {target} : {e}")
            current_peer_idx = (current_peer_idx + 1) % len(PEERS)
            print(f"🔄 [CLIENT] Passage au pair suivant dans 2s...")
            time.sleep(2)

if __name__ == "__main__":
    download_with_fallback("test.txt", 5)