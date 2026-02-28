from nacl.signing import SigningKey
from nacl.public import PrivateKey
import os
import json
from nacl.secret import SecretBox
def generate_keys():
    """Génère une paire de clés Ed25519 pour le nœud"""
    
    # Génère la clé privée (secrète)
    signing_key = SigningKey.generate()
    
    # Déduit la clé publique depuis la clé privée
    verify_key = signing_key.verify_key
    
    # Convertit en hexadécimal pour pouvoir les lire
    private_key_hex = signing_key.encode().hex()
    public_key_hex = verify_key.encode().hex()
    
    return {
        "private_key": private_key_hex,
        "public_key": public_key_hex
    }

def save_keys(keys, filename="my_keys.json"):
    """Sauvegarde les clés dans un fichier"""
    with open(filename, "w") as f:
        json.dump(keys, f, indent=4)
    print(f"✅ Clés sauvegardées dans {filename}")

def load_keys(filename="my_keys.json"):
    """Charge les clés depuis un fichier"""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    else:
        print("❌ Aucune clé trouvée, génération en cours...")
        keys = generate_keys()
        save_keys(keys, filename)
        return keys

# Test — génère et affiche les clés
if __name__ == "__main__":
    print("🔑 Génération des clés...")
    keys = generate_keys()
    print(f"Clé publique  : {keys['public_key']}")
    print(f"Clé privée    : {keys['private_key']}")
    save_keys(keys)
    print("✅ Terminé !")
    from nacl.secret import SecretBox
from nacl.utils import random as nacl_random

def encrypt_message(message, session_key):
    """Chiffre un message avec AES-256-GCM"""
    
    # Convertit le message en bytes si c'est du texte
    if isinstance(message, str):
        message = message.encode("utf-8")
    
    # Crée une boîte secrète avec la clé de session
    box = SecretBox(session_key)
    
    # Chiffre le message (nonce généré automatiquement)
    encrypted = box.encrypt(message)
    
    print(f"🔒 Message chiffré avec succès !")
    return encrypted

def decrypt_message(encrypted_message, session_key):
    """Déchiffre un message avec AES-256-GCM"""
    
    # Crée une boîte secrète avec la clé de session
    box = SecretBox(session_key)
    
    # Déchiffre le message
    decrypted = box.decrypt(encrypted_message)
    
    # Reconvertit en texte
    message = decrypted.decode("utf-8")
    
    print(f"🔓 Message déchiffré : {message}")
    return message

def generate_session_key():
    """Génère une clé de session aléatoire"""
    return nacl_random(SecretBox.KEY_SIZE)

# Test du chiffrement
if __name__ == "__main__":
    print("\n--- TEST CHIFFREMENT ---")
    
    # Génère une clé de session
    session_key = generate_session_key()
    print(f"🗝️  Clé de session générée")
    
    # Message à chiffrer
    message_original = "Bonjour Archipel ! Ceci est un message secret."
    print(f"📝 Message original : {message_original}")
    
    # Chiffre le message
    message_chiffre = encrypt_message(message_original, session_key)
    
    # Déchiffre le message
    message_dechiffre = decrypt_message(message_chiffre, session_key)
    
    # Vérifie que c'est identique
    if message_original == message_dechiffre:
        print("✅ Chiffrement/Déchiffrement fonctionnel !")
    else:
        print("❌ Erreur !")