import socket
import threading
import os
from colorama import Fore, Style
from src.network.protocol import receive_tlv, MSG_CHAT_TEXT, MSG_MANIFEST, MSG_FILE_CHUNK
from src.security.handshake import HandshakeManager
from src.security.encryption import ArchipelEncryption

def handle_client(conn, addr, shared_folder):
    """Gère une connexion entrante : Sécurisation + Réception de données"""
    current_filename = None
    
    try:
        # 1. ÉTAPE DE SÉCURISATION (Handshake RSA -> AES)
        h_manager = HandshakeManager()
        key = h_manager.do_server_handshake(conn)
        if not key:
            print(f"{Fore.RED}❌ Échec de la sécurisation avec {addr}")
            return
            
        crypto = ArchipelEncryption(key)

        # 2. BOUCLE DE RÉCEPTION (Écoute les messages TLV)
        while True:
            m_type, enc_val = receive_tlv(conn)
            if m_type is None:
                break # Déconnexion propre

            # --- TYPE : MESSAGE DE CHAT (0x05) ---
            if m_type == MSG_CHAT_TEXT:
                decrypted_msg = crypto.decrypt_data(enc_val).decode('utf-8')
                print(f"\n{Fore.CYAN}💬 [MSG REÇU de {addr[0]}]{Style.RESET_ALL} : {decrypted_msg}")
                print(f"{Fore.YELLOW}ARCHIPEL > {Style.RESET_ALL}", end="", flush=True)

            # --- TYPE : MANIFEST DE FICHIER (0x03) ---
            elif m_type == MSG_MANIFEST:
                info = crypto.decrypt_data(enc_val).decode().split(":")
                current_filename = info[0]
                print(f"\n{Fore.BLUE}📥 Début de réception du fichier : {current_filename}")
                
                # Créer ou vider le fichier dans le dossier partagé
                file_path = os.path.join(shared_folder, current_filename)
                open(file_path, "wb").close()

            # --- TYPE : BLOC DE FICHIER (0x02) ---
            elif m_type == MSG_FILE_CHUNK:
                if current_filename:
                    raw_chunk = crypto.decrypt_data(enc_val)
                    file_path = os.path.join(shared_folder, current_filename)
                    with open(file_path, "ab") as f:
                        f.write(raw_chunk)
                else:
                    print(f"{Fore.RED}⚠️ Bloc reçu sans manifest préalable !")

    except Exception as e:
        # On ne print rien ici pour éviter de polluer la console lors d'une déco normale
        pass 
    finally:
        conn.close()

def start_node(port, shared_folder="shared_files"):
    """Démarre le serveur TCP ARCHIPEL"""
    # Création du dossier de réception si nécessaire
    if not os.path.exists(shared_folder):
        os.makedirs(shared_folder)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind(('0.0.0.0', port))
        s.listen(5)
        print(f"{Fore.GREEN}✅ Serveur TCP actif sur le port {port}")
        print(f"{Fore.WHITE}📂 Dossier de réception : {os.path.abspath(shared_folder)}")
        
        while True:
            c, a = s.accept()
            # Chaque connexion est gérée dans un nouveau Thread
            threading.Thread(target=handle_client, args=(c, a, shared_folder), daemon=True).start()
    except Exception as e:
        print(f"{Fore.RED}❌ Erreur serveur : {e}")
    finally:
        s.close()