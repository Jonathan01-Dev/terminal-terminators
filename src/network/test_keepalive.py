import socket
import time
import threading
from src.network.protocol import format_tlv, receive_tlv, MSG_PING, MSG_PONG

def ping_thread(sock):
    while True:
        try:
            time.sleep(15)
            print("📤 Envoi PING...")
            sock.sendall(format_tlv(MSG_PING, b"PING"))
        except: break

def run_test():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', 5050))
        print("✅ Connecté au serveur.")
        threading.Thread(target=ping_thread, args=(s,), daemon=True).start()
        while True:
            m_type, val = receive_tlv(s)
            if m_type == MSG_PONG: print("📥 PONG reçu !")
            elif m_type is None: break
    except Exception as e: print(f"❌ Erreur : {e}")
    finally: s.close()

if __name__ == "__main__":
    run_test()