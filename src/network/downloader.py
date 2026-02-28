import socket
from src.network.protocol import format_tlv, receive_tlv, MSG_REQUEST_CHUNK, MSG_FILE_CHUNK

class ArchipelDownloader:
    def __init__(self, manifest, peer_list):
        self.manifest = manifest
        self.peer_list = peer_list # Liste d'IPs [(ip1, port1), (ip2, port2)]
        self.downloaded_chunks = 0
        self.total_chunks = manifest['total_chunks']

    def download_file(self):
        current_peer_idx = 0
        
        while self.downloaded_chunks < self.total_chunks:
            peer = self.peer_list[current_peer_idx]
            print(f"📡 Tentative avec le pair {peer}...")
            
            try:
                # Connexion et Handshake (simplifié ici)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(peer)
                
                # On demande les blocs restants
                for i in range(self.downloaded_chunks, self.total_chunks):
                    # Alice demande le bloc i
                    request = f"{self.manifest['hash']}:{i}".encode()
                    s.sendall(format_tlv(MSG_REQUEST_CHUNK, request))
                    
                    # Réception du bloc
                    m_type, data = receive_tlv(s)
                    if m_type == MSG_FILE_CHUNK:
                        self.save_chunk(i, data)
                        self.downloaded_chunks += 1
                    else:
                        raise Exception("Mauvais format de bloc")
                
                s.close()
            except Exception as e:
                print(f"⚠️ Pair {peer} déconnecté ou erreur. Passage au suivant...")
                current_peer_idx = (current_peer_idx + 1) % len(self.peer_list)
                if current_peer_idx == 0:
                    print("❌ Plus aucun pair disponible.")
                    break

    def save_chunk(self, index, data):
        # Logique pour écrire le bloc au bon endroit dans le fichier
        with open(f"downloads/{self.manifest['filename']}", "ab") as f:
            f.write(data)