import socket
import json
import time
import threading

MULTICAST_GROUP = '224.0.0.1'
MULTICAST_PORT = 6000

def start_discovery(my_tcp_port):
    """
    Diffuse la présence du nœud et écoute les autres.
    """
    # 1. Socket pour l'ÉCOUTE (UDP Multicast)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', MULTICAST_PORT))
    
    # Rejoindre le groupe multicast
    mreq = socket.inet_aton(MULTICAST_GROUP) + socket.inet_aton('0.0.0.0')
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    # 2. Fonction interne pour la DIFFUSION
    def broadcast_presence():
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broadcast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        
        while True:
            message = json.dumps({"port": my_tcp_port, "status": "online"}).encode()
            broadcast_sock.sendto(message, (MULTICAST_GROUP, MULTICAST_PORT))
            time.sleep(5)

    # Lancer le thread de diffusion
    threading.Thread(target=broadcast_presence, daemon=True).start()

    print(f"📡 Nœud actif (TCP Port {my_tcp_port}). Écoute des pairs...")
    
    # 3. Boucle d'écoute des autres nœuds
    peers = set()
    while True:
        data, addr = sock.recvfrom(1024)
        info = json.loads(data.decode())
        peer_id = f"{addr[0]}:{info['port']}"
        
        # On ne s'ajoute pas soi-même
        if info['port'] != my_tcp_port:
            if peer_id not in peers:
                peers.add(peer_id)
                print(f"✨ Nouveau pair détecté ! -> {peer_id} | Total : {len(peers)}")

if __name__ == "__main__":
    # Permet de tester en lançant : python discovery.py [PORT]
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5050
    start_discovery(port)