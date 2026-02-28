import socket
from src.network.protocol import format_tlv

# On simule l'envoi d'un "Type 1" (Texte)
data = "Secret de l'Archipel".encode()
package = format_tlv(1, data)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 5050))
s.sendall(package)
print(s.recv(1024).decode())
s.close()