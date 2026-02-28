import socket
import threading
import os
import json
from src.network.protocol import receive_tlv, format_tlv, MSG_MANIFEST, MSG_FILE_CHUNK, MSG_REQUEST_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

# Dossiers de stockage
SHARED_FOLDER = "shared_files/" # Fichiers que Bob accepte de partager
MANIFEST_FOLDER = ".archipel/manifests/"

def ensure_dirs():
    os.makedirs(SHARED_FOLDER, exist_ok=True)
    os.makedirs(MANIFEST_FOLDER, exist_ok=True)

def handle_client(conn, addr):
    ensure_dirs()
    security_mgr = HandshakeManager()
    session_key = security_mgr.do_server_handshake(conn)
    
    if not session_key:
        conn.close()
        return

    crypto = ArchipelEncryption(session_key)
    print(f"🔒 [SECURE] Prêt pour requêtes de blocs avec {addr}")

    try:
        while True:
            m_type, encrypted_val = receive_tlv(conn)
            if m_type is None: break

            # CAS : REQUÊTE DE BLOC SPÉCIFIQUE (Fallback / P2P)
            if m_type == MSG_REQUEST_CHUNK:
                # 1. Déchiffrer la requête (format attendu : "nom_du_fichier:index_du_bloc")
                request_raw = crypto.decrypt_data(encrypted_val).decode('utf-8')
                filename, chunk_idx = request_raw.split(":")
                chunk_idx = int(chunk_idx)
                
                file_path = os.path.join(SHARED_FOLDER, filename)
                
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        # 2. SE DÉPLACER au bon endroit dans le fichier
                        # Position = Index du bloc * Taille d'un bloc (4096)
                        f.seek(chunk_idx * 4096)
                        chunk_data = f.read(4096)
                        
                        if chunk_data:
                            # 3. Renvoyer le bloc chiffré
                            enc_chunk = crypto.encrypt_data(chunk_data)
                            conn.sendall(format_tlv(MSG_FILE_CHUNK, enc_chunk))
                            print(f"📤 Envoyé bloc {chunk_idx} de {filename}")
                else:
                    print(f"⚠️ Fichier {filename} non trouvé dans {SHARED_FOLDER}")

    except Exception as e:
        print(f"❌ Erreur serveur : {e}")
    finally:
        conn.close()

def start_bob():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5050))
    server.listen(5)
    print("👤 Bob est prêt à servir des morceaux de fichiers...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_bob()