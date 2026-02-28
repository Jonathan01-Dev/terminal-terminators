from src.security.wot import WebOfTrust
from src.security.handshake import HandshakeManager
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def generate_recommendation(recommender_mgr, new_peer_id):
    """Simule Bob qui signe une recommandation pour Charlie"""
    data = f"Bob trusts {new_peer_id}".encode()
    signature = recommender_mgr.private_key.sign(
        data,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
        hashes.SHA256()
    )
    return signature

def run_wot_demo():
    print("--- 🛡️ TEST WEB OF TRUST ARCHIPEL ---")
    
    # 1. Création des identités
    alice_wot = WebOfTrust("Alice")
    bob_mgr = HandshakeManager()     # Bob a ses clés RSA
    charlie_mgr = HandshakeManager() # Charlie a ses clés RSA

    # 2. CONFIANCE DIRECTE : Alice ajoute Bob manuellement
    print("\nÉtape 1 : Alice ajoute Bob à sa liste de confiance.")
    alice_wot.add_trust("Bob", bob_mgr.get_public_key_pem(), level=1)

    # 3. PROPAGATION : Bob recommande Charlie à Alice
    print("\nÉtape 2 : Bob signe une recommandation pour Charlie.")
    sig_bob_for_charlie = generate_recommendation(bob_mgr, "Charlie")
    
    print("Étape 3 : Alice vérifie la recommandation de Bob.")
    success = alice_wot.verify_recommendation(
        recommender_id="Bob",
        new_peer_id="Charlie",
        new_pub_key=charlie_mgr.get_public_key_pem(),
        signature=sig_bob_for_charlie
    )
    
    if success:
        print("✅ Alice fait maintenant confiance à Charlie (Niveau 2) via Bob !")
    else:
        print("❌ Échec de la recommandation.")

    # 4. RÉVOCATION : Alice décide que Bob n'est plus fiable
    print("\nÉtape 4 : Alice révoque Bob (incident de sécurité).")
    alice_wot.revoke("Bob")
    
    if "Bob" not in alice_wot.trusted_peers:
        print("🛡️ Succès : Bob a été banni de la liste de confiance d'Alice.")

if __name__ == "__main__":
    run_wot_demo()