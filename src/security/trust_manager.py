import json
import os

TRUSTED_FILE = "trusted_peers.json"

def add_to_trust(node_id):
    """Ajoute un Node ID à la liste de confiance"""
    trusted = get_all_trusted()
    if node_id not in trusted:
        trusted.append(node_id)
        with open(TRUSTED_FILE, "w") as f:
            json.dump(trusted, f, indent=4)
        return True
    return False

def get_all_trusted():
    """Récupère la liste des IDs approuvés"""
    if not os.path.exists(TRUSTED_FILE):
        return []
    try:
        with open(TRUSTED_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def is_trusted(node_id):
    """Vérifie si un ID est dans la liste"""
    return node_id in get_all_trusted()