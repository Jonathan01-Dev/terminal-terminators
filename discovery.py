import socket
import struct
import threading
import time

peers = {}

MULTICAST_GROUP = "239.255.42.42"
PORT = 4242

# 🔹 Envoie HELLO toutes les 5 secondes
def send_hello():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ttl = struct.pack('b', 1)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)

    while True:
        message = "HELLO"
        sock.sendto(message.encode(), (MULTICAST_GROUP, PORT))
        print("HELLO envoyé")
        time.sleep(5)

# 🔹 Écoute les HELLO
def listen_hello():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', PORT))

    mreq = struct.pack("4sl", socket.inet_aton(MULTICAST_GROUP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    while True:
        data, address = sock.recvfrom(1024)
        ip = address[0]

        # On met à jour le timestamp à chaque HELLO
        peers[ip] = time.time()

        print("Peer actif :", ip)
        print("Table actuelle :", peers)

# 🔹 Nettoyage des peers inactifs
def clean_peers():
    while True:
        now = time.time()

        for ip in list(peers.keys()):
            if now - peers[ip] > 15:
                print("Peer supprimé :", ip)
                del peers[ip]

        time.sleep(5)

# 🔹 Lancer les threads
threading.Thread(target=send_hello).start()
threading.Thread(target=listen_hello).start()
threading.Thread(target=clean_peers).start()
