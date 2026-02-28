from cryptography.hazmat.primitives.asymmetric import rsa
from tofu_manager import verify_or_save_peer

# On simule la clé d’un pair distant
remote_private = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

remote_public = remote_private.public_key()

# Test TOFU
verify_or_save_peer("node1", remote_public)ss