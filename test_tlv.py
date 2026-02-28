import socket
from src.network.protocol import format_tlv
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('127.0.0.1', 5050))
    packet = format_tlv(1, b"Test TLV Archipel")
    s.sendall(packet)
    print("📦 Paquet envoyé !")
    print("📥 Reponse:", s.recv(1024).decode())
except Exception as e:
    print(f"❌ Erreur: {e}")
finally:
    s.close()
