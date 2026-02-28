import os
from nacl.signing import SigningKey
from nacl.encoding import HexEncoder

# Le fichier .key est dans le .gitignore, donc il ne sera pas publié
PRIVATE_KEY_FILE = "my_identity.key"

def get_or_create_identity():
    if not os.path.exists(PRIVATE_KEY_FILE):
        signing_key = SigningKey.generate()
        with open(PRIVATE_KEY_FILE, "wb") as f:
            f.write(signing_key.encode(encoder=HexEncoder))
    else:
        with open(PRIVATE_KEY_FILE, "rb") as f:
            signing_key = SigningKey(f.read(), encoder=HexEncoder)

    verify_key = signing_key.verify_key
    public_key_hex = verify_key.encode(encoder=HexEncoder).decode('utf-8')
    
    return signing_key, public_key_hex