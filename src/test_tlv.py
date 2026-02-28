import socket
from src.network.protocol import format_tlv

def run_test():
    target_ip = '127.0.0.1'
    target_port = 5050
    
    print("🚀 Préparation du paquet TLV...")
    # Type 1 = Texte, Donnée = "Hello Archipel"
    data = "Test du protocole TLV réussi !".encode('utf-8')
    packet = format_tlv(1, data)
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((target_ip, target_port))
            print(f"📡 Connexion à {target_ip}:{target_port}")
            
            s.sendall(packet)
            print("📤 Paquet envoyé.")
            
            response = s.recv(1024)
            print(f"📥 Réponse du serveur : {response.decode()}")
            
    except ConnectionRefusedError:
        print("❌ Erreur : Le serveur n'est pas lancé sur le port 5050.")
    except Exception as e:
        print(f"❌ Erreur inattendue : {e}")

if __name__ == "__main__":
    run_test()