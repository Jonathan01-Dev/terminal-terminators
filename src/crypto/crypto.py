import os
import json
import hashlib
import hmac
import time
from nacl.signing import SigningKey, VerifyKey
from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.utils import random as nacl_random


def generate_keys():
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    return {
        "private_key": signing_key.encode().hex(),
        "public_key": verify_key.encode().hex()
    }

def load_or_generate_keys(filename="node.key"):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            data = json.load(f)
        print(f"✅ Clés chargées depuis {filename}")
        return data
    else:
        print("⚠️ Génération de nouvelles clés...")
        keys = generate_keys()
        with open(filename, "w") as f:
            json.dump(keys, f, indent=4)
        print(f"✅ Clés sauvegardées dans {filename}")
        return keys

def generate_session_keypair():
    private_key = PrivateKey.generate()
    public_key = private_key.public_key
    return {
        "private": private_key,
        "public": bytes(public_key).hex()
    }

def compute_shared_secret(my_private_key, their_public_key_hex):
    their_public_key = PublicKey(bytes.fromhex(their_public_key_hex))
    box = Box(my_private_key, their_public_key)
    shared_secret = bytes(box)
    print(f"🤝 Secret partagé : {shared_secret.hex()[:20]}...")
    return shared_secret

def derive_session_key(shared_secret):
    prk = hmac.new(b"archipel-v1", shared_secret, hashlib.sha256).digest()
    session_key = hmac.new(prk, b"session-key-v1", hashlib.sha256).digest()
    print(f"🔑 Clé de session : {session_key.hex()[:20]}...")
    return session_key

def handshake_initiator(my_permanent_keys):
    ephemeral = generate_session_keypair()
    hello = {
        "type": "HELLO",
        "ephemeral_pub": ephemeral["public"],
        "sender_id": my_permanent_keys["public_key"],
        "timestamp": int(time.time())
    }
    signing_key = SigningKey(bytes.fromhex(my_permanent_keys["private_key"]))
    message_bytes = json.dumps(hello).encode("utf-8")
    hello["signature"] = signing_key.sign(message_bytes).signature.hex()
    print(f"📤 HELLO envoyé : {ephemeral['public'][:20]}...")
    return hello, ephemeral["private"]

def handshake_responder(hello_message, my_permanent_keys):
    try:
        verify_key = VerifyKey(bytes.fromhex(hello_message["sender_id"]))
        msg_without_sig = {k: v for k, v in hello_message.items() if k != "signature"}
        message_bytes = json.dumps(msg_without_sig).encode("utf-8")
        verify_key.verify(message_bytes, bytes.fromhex(hello_message["signature"]))
        print("✅ Signature vérifiée !")
    except Exception:
        print("❌ Signature invalide !")
        return None, None
    ephemeral = generate_session_keypair()
    shared_secret = compute_shared_secret(ephemeral["private"], hello_message["ephemeral_pub"])
    session_key = derive_session_key(shared_secret)
    reply = {
        "type": "HELLO_REPLY",
        "ephemeral_pub": ephemeral["public"],
        "sender_id": my_permanent_keys["public_key"],
        "timestamp": int(time.time())
    }
    signing_key = SigningKey(bytes.fromhex(my_permanent_keys["private_key"]))
    message_bytes = json.dumps(reply).encode("utf-8")
    reply["signature"] = signing_key.sign(message_bytes).signature.hex()
    print(f"📤 HELLO_REPLY envoyé : {ephemeral['public'][:20]}...")
    return reply, session_key

def encrypt_message(session_key, plaintext):
    from Crypto.Cipher import AES
    if isinstance(plaintext, str):
        plaintext = plaintext.encode("utf-8")
    nonce = os.urandom(12)
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    print(f"🔒 Message chiffré !")
    return {
        "nonce": nonce.hex(),
        "ciphertext": ciphertext.hex(),
        "tag": tag.hex()
    }

def decrypt_message(session_key, encrypted_data):
    from Crypto.Cipher import AES
    nonce = bytes.fromhex(encrypted_data["nonce"])
    ciphertext = bytes.fromhex(encrypted_data["ciphertext"])
    tag = bytes.fromhex(encrypted_data["tag"])
    cipher = AES.new(session_key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    message = plaintext.decode("utf-8")
    print(f"🔓 Message déchiffré : {message}")
    return message


if __name__ == "__main__":
    print("\n" + "="*50)
    print("   🔐 TEST COMPLET SPRINT 2")
    print("="*50)

    print("\n📋 Chargement des clés...")
    alice_keys = load_or_generate_keys("alice.key")
    bob_keys = load_or_generate_keys("bob.key")

    print("\n🤝 Handshake en cours...")
    hello, alice_ephemeral_priv = handshake_initiator(alice_keys)
    reply, session_key_bob = handshake_responder(hello, bob_keys)

    shared = compute_shared_secret(alice_ephemeral_priv, reply["ephemeral_pub"])
    session_key_alice = derive_session_key(shared)

    print("\n💬 Test chiffrement...")
    message = "Bonjour Bob, ceci est secret !"
    print(f"📝 Message original : {message}")

    encrypted = encrypt_message(session_key_alice, message)
    decrypted = decrypt_message(session_key_bob, encrypted)

    if message == decrypted:
        print("\n✅ SPRINT 2 VALIDÉ — Chiffrement E2E fonctionnel !")
    else:
        print("\n❌ Erreur !")