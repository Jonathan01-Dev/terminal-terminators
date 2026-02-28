import socket
import threading
from src.network.protocol import receive_tlv, format_tlv, MSG_PING, MSG_PONG, MSG_TEXT

def handle_client(conn, addr):
    print(f"🧵 [THREAD START] Connexion : {addr}")
    try:
        while True:
            msg_type, value = receive_tlv(conn)
            if msg_type is None: break
                
            if msg_type == MSG_PING:
                print(f"💓 PING de {addr} -> Réponse PONG")
                conn.sendall(format_tlv(MSG_PONG, b"PONG"))
            elif msg_type == MSG_TEXT:
                print(f"📩 Message de {addr}: {value.decode()}")
                conn.sendall(format_tlv(MSG_TEXT, b"ACK"))
    finally:
        conn.close()
        print(f"🔌 [THREAD END] Déconnexion : {addr}")

def start_tcp_server(port=5050):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', port))
    server.listen(5)
    print(f"📦 Serveur Archipel actif sur le port {port}...")
    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_tcp_server()