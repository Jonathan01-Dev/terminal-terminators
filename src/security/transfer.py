import json
import hashlib
import os
from src.network.protocol import format_tlv, MSG_MANIFEST

def prepare_manifest_packet(file_path, crypto):
    # 1. Extraire les infos du fichier
    file_name = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)
    
    # 2. Calculer le Hash (SHA-256)
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    # 3. Créer le dictionnaire JSON
    manifest_dict = {
        "filename": file_name,
        "size": file_size,
        "hash": sha256_hash.hexdigest(),
        "total_chunks": (file_size // 4096) + 1
    }
    
    # 4. Sérialiser en JSON puis encoder en bytes
    json_bytes = json.dumps(manifest_dict).encode('utf-8')
    
    # 5. CHIFFRER avec ta clé de session AES
    encrypted_manifest = crypto.encrypt_data(json_bytes)
    
    # 6. Emballer en TLV Type 8
    return format_tlv(MSG_MANIFEST, encrypted_manifest)