try:
    import nacl.secret
    import Crypto
    print("✅ Succès : PyNaCl et PyCryptodome sont bien installés !")
except ImportError as e:
    print(f"❌ Erreur : Il manque une bibliothèque : {e}")