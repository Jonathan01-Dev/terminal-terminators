import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class WebOfTrust:
    def __init__(self, my_id):
        self.my_id = my_id
        self.trusted_peers = {} # {peer_id: {"pub_key": key, "level": 1}}
        self.revocation_list = set()

    def add_trust(self, peer_id, pub_key_pem, level=1):
        """Ajoute un pair à la liste de confiance locale."""
        self.trusted_peers[peer_id] = {
            "key": pub_key_pem,
            "level": level
        }
        print(f"🤝 Confiance établie avec {peer_id} (Niveau {level})")

    def verify_recommendation(self, recommender_id, new_peer_id, new_pub_key, signature):
        """Vérifie si une recommandation signée est valide."""
        if recommender_id not in self.trusted_peers:
            return False # On ne connaît pas le recommandeur
        
        # Charger la clé du recommandeur
        recommender_key = serialization.load_pem_public_key(self.trusted_peers[recommender_id]["key"])
        
        # Vérifier la signature
        data = f"{recommender_id} trusts {new_peer_id}".encode()
        try:
            recommender_key.verify(
                signature,
                data,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            # Propagation : Nouveau niveau = Niveau du recommandeur + 1
            new_level = self.trusted_peers[recommender_id]["level"] + 1
            self.add_trust(new_peer_id, new_pub_key, new_level)
            return True
        except:
            return False

    def revoke(self, peer_id):
        """Révocation immédiate d'un pair."""
        if peer_id in self.trusted_peers:
            del self.trusted_peers[peer_id]
            self.revocation_list.add(peer_id)
            print(f"🚫 Pair {peer_id} révoqué et banni !")