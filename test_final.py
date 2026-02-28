import hashlib, os, time, socket, sys
sys.path.append(os.getcwd())
from src.network.protocol import receive_tlv, format_tlv, MSG_REQUEST_CHUNK, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

PEERS = [('127.0.0.1', 5060), ('127.0.0.1', 5061)]
FILENAME = "document_test.pdf"
TOTAL_CHUNKS = 2560 

def get_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(4096), b""): h.update(b)
    return h.hexdigest()

def start_download():
    chunks_received = 0
    peer_idx = 0
    dest = f"downloads/{FILENAME}"
    os.makedirs("downloads", exist_ok=True)
    if os.path.exists(dest): os.remove(dest)

    print(f"🚀 [ALICE] Démarrage du téléchargement...")

    while chunks_received < TOTAL_CHUNKS:
        target = PEERS[peer_idx]
        print(f"📡 Tentative sur {target}...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect(target)
            
            key = HandshakeManager.do_client_handshake(s)
            crypto = ArchipelEncryption(key)
            print(f"🔒 Session sécurisée. Reprise au bloc {chunks_received}")

            while chunks_received < TOTAL_CHUNKS:
                req = f"{FILENAME}:{chunks_received}".encode()
                s.sendall(format_tlv(MSG_REQUEST_CHUNK, crypto.encrypt_data(req)))
                
                m_type, enc_data = receive_tlv(s)
                if m_type == MSG_FILE_CHUNK:
                    with open(dest, "ab") as f:
                        f.write(crypto.decrypt_data(enc_data))
                    chunks_received += 1
                    if chunks_received % 100 == 0:
                        print(f"📦 Avancement : {chunks_received}/{TOTAL_CHUNKS}")
                else: break
            s.close()
        except Exception as e:
            print(f"⚠️ Échec sur {target}: {e}")
            peer_idx = (peer_idx + 1) % len(PEERS)
            time.sleep(1)

    print("\n🏁 Terminé. Vérification SHA-256...")
    orig = f"shared_files_bob/{FILENAME}"
    if os.path.exists(orig):
        s_orig, s_recv = get_sha256(orig), get_sha256(dest)
        print(f"✅ Original : {s_orig}\n✅ Reçu     : {s_recv}")
        print("🏆 SUCCÈS !" if s_orig == s_recv else "❌ CORROMPU")

if __name__ == "__main__":
    start_download()
