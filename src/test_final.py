import hashlib
import os
import time
import socket
import sys

# On s'assure que Python trouve le dossier src
sys.path.append(os.getcwd())

from src.network.protocol import receive_tlv, format_tlv, MSG_REQUEST_CHUNK, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

# Configuration pour ton test
PEERS = [('127.0.0.1', 5060), ('127.0.0.1', 5061)]
FILENAME = "document_test.pdf"
TOTAL_CHUNKS = 2560 

def get_sha256(file_path):
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return sha.hexdigest()

def start_download():
    chunks_received = 0
    current_peer = 0
    dest_path = f"downloads/{FILENAME}"
    
    os.makedirs("downloads", exist_ok=True)
    if os.path.exists(dest_path): os.remove(dest_path)

    print(f"🚀 [ALICE] Démarrage du téléchargement de {FILENAME}...")

    while chunks_received < TOTAL_CHUNKS:
        target = PEERS[current_peer]
        print(f"📡 Tentative sur {target}...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect(target)
            
            key = HandshakeManager.do_client_handshake(s)
            crypto = ArchipelEncryption(key)
            print(f"🔒 Connexion sécurisée avec {target}")

            while chunks_received < TOTAL_CHUNKS:
                req = f"{FILENAME}:{chunks_received}".encode()
                s.sendall(format_tlv(MSG_REQUEST_CHUNK, crypto.encrypt_data(req)))
                
                m_type, enc_data = receive_tlv(s)
                if m_type == MSG_FILE_CHUNK:
                    with open(dest_path, "ab") as f:
                        f.write(crypto.decrypt_data(enc_data))
                    chunks_received += 1
                    
                    if chunks_received % 50 == 0:
                        print(f"📦 Avancement : {chunks_received}/{TOTAL_CHUNKS}", end="\r")
                else: 
                    break
            s.close()
        except Exception as e:
            print(f"\n⚠️ Pair {target} indisponible ({e}). Bascule...")
            current_peer = (current_peer + 1) % len(PEERS)
            time.sleep(1)

    print("\n\n🏁 Transfert terminé ! Vérification SHA-256...")
    
    orig_path = f"shared_files_bob/{FILENAME}"
    if os.path.exists(orig_path):
        orig_sha = get_sha256(orig_path)
        recv_sha = get_sha256(dest_path)
        print(f"✅ Original : {orig_sha}")
        print(f"✅ Reçu     : {recv_sha}")
        if orig_sha == recv_sha:
            print("\n🏆 SUCCÈS : Les empreintes sont identiques !")
        else:
            print("\n❌ ERREUR : Fichiers différents.")
    else:
        print("⚠️ Fichier source introuvable pour comparaison.")

if __name__ == "__main__":
    start_download()