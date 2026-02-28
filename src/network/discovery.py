import socket
import json
import time
import threading
from colorama import Fore, Style

# Paramètres réseau
MULTICAST_GROUP = '224.0.0.1'
MULTICAST_PORT = 6000

# Table globale : { "IP:Port": Timestamp_Dernière_Vue }
PEER_TABLE = {}

def start_discovery(my_tcp_port):
    """Initialise la découverte automatique (Multicast)"""
    
    # Configuration du socket d'écoute
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        sock.bind(('', MULTICAST_PORT))
    except Exception as e:
        print(f"⚠️ Erreur UDP Bind: {e}")
        return

    # Rejoindre le groupe Multicast
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def broadcast_presence():
        """Dit 'Je suis là' toutes les 5 secondes"""
        b_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        b_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        while True:
            try:
                msg = json.dumps({"port": my_tcp_port}).encode()
                b_sock.sendto(msg, (MULTICAST_GROUP, MULTICAST_PORT))
            except: pass
            time.sleep(5)

    def listen_for_peers():
        """Écoute et met à jour la Peer Table"""
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                info = json.loads(data.decode())
                peer_id = f"{addr[0]}:{info['port']}"
                
                # Filtrer soi-même (Simple vérification de port si localhost)
                if not (addr[0] == '127.0.0.1' and info['port'] == my_tcp_port):
                    PEER_TABLE[peer_id] = time.time()
            except: pass

    # Lancement des processus en arrière-plan
    threading.Thread(target=broadcast_presence, daemon=True).start()
    threading.Thread(target=listen_for_peers, daemon=True).start()

def get_formatted_peers_data():
    """Prépare les données pour le tableau CLI"""
    now = time.time()
    rows = []
    
    for peer_id, last_seen in PEER_TABLE.items():
        delay = int(now - last_seen)
        
        # Statut visuel
        if delay < 15:
            status = f"{Fore.GREEN}● Online{Style.RESET_ALL}"
        else:
            status = f"{Fore.RED}○ Offline{Style.RESET_ALL}"
            
        rows.append([peer_id, status, f"{delay}s ago", "AES-256-GCM"])
    
    return rows