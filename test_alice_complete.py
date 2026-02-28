import socket
import os
import json
import hashlib
from src.network.protocol import format_tlv, MSG_MANIFEST, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

def get_file_info(path):
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return {
        "filename": os.path.basename(path),
        "size": os.path.getsize(path),
        "hash": sha.hexdigest(),
        "total_chunks": (os.path.getsize(path) // 4096) + 1
    }

def send_full_file(file_path):
    if not os.path.exists(file_path):
        print(f"❌ Fichier {file_path} introuvable.")
        return

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 5050))
        print("📡 Connexion établie. Lancement du Handshake...")
        
        # RÉCUPÉRATION DE LA CLÉ
        key = HandshakeManager.do_client_handshake(s)
        
        if key is None:
            print("❌ ERREUR : La clé de session est vide (None). Vérifiez le serveur.")
            return

        crypto = ArchipelEncryption(key)
        print("✅ Clé de session activée. Envoi du manifeste...")

        # 1. Envoi Manifeste
        info = get_file_info(file_path)
        manifest_enc = crypto.encrypt_data(json.dumps(info).encode('utf-8'))
        s.sendall(format_tlv(MSG_MANIFEST, manifest_enc))

        # 2. Envoi Chunks
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(4096)
                if not chunk: break
                s.sendall(format_tlv(MSG_FILE_CHUNK, crypto.encrypt_data(chunk)))
                print(".", end="", flush=True)

        print("\n🏁 [SUCCÈS] Transfert terminé !")
    except Exception as e:
        print(f"\n❌ Erreur critique : {e}")
    finally:
        s.close()

if __name__ == "__main__":
    # S'assurer que test.txt existe
    with open("test.txt", "w") as f: f.write("Contenu de test pour Archipel " * 100)
    send_full_file("test.txt")