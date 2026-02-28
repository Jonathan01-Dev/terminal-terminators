import socket
import os
import json
import hashlib
from src.network.protocol import format_tlv, MSG_MANIFEST, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

def get_file_info(path):
    name = os.path.basename(path)
    size = os.path.getsize(path)
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha.update(chunk)
    return {
        "filename": name,
        "size": size,
        "hash": sha.hexdigest(),
        "total_chunks": (size // 4096) + 1
    }

def send_full_file(file_path):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('127.0.0.1', 5050))
    
    # 1. Sécurité
    key = HandshakeManager.do_client_handshake(s)
    crypto = ArchipelEncryption(key)

    # 2. Manifeste
    info = get_file_info(file_path)
    manifest_bytes = json.dumps(info).encode('utf-8')
    s.sendall(format_tlv(MSG_MANIFEST, crypto.encrypt_data(manifest_bytes)))
    print(f"🚀 Manifeste envoyé pour {info['filename']}")

    # 3. Chunks
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk: break
            s.sendall(format_tlv(MSG_FILE_CHUNK, crypto.encrypt_data(chunk)))
            print(".", end="", flush=True)

    print("\n🏁 Envoi terminé !")
    s.close()

if __name__ == "__main__":
    # Test avec un fichier quelconque
    with open("secret_alice.txt", "w") as f:
        f.write("Ceci est un secret très important envoyé via Archipel." * 50)
    send_full_file("secret_alice.txt")