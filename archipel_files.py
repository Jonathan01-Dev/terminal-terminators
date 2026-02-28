import os
import hashlib
import json

CHUNK_SIZE = 512 * 1024  # 512 KB

def calculate_hash(data):
    return hashlib.sha256(data).hexdigest()

def split_file(file_path):
    if not os.path.exists(file_path):
        print("❌ Fichier introuvable.")
        return

    os.makedirs("chunks", exist_ok=True)

    manifest = {
        "filename": os.path.basename(file_path),
        "chunks": []
    }

    with open(file_path, "rb") as f:
        index = 0
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break

            chunk_name = f"chunk_{index}.bin"
            chunk_path = os.path.join("chunks", chunk_name)

            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(chunk)

            manifest["chunks"].append({
                "id": index,
                "name": chunk_name,
                "hash": calculate_hash(chunk)
            })
            index += 1

    with open("manifest.json", "w") as m:
        json.dump(manifest, m, indent=4)

    print(f"✅ Découpage terminé : {index} chunks créés.")

def reassemble_file():
    # 1. Vérification du manifest
    if not os.path.exists("manifest.json"):
        print("❌ Fichier introuvable.")
        return # Arrête tout ici

    with open("manifest.json", "r") as m:
        manifest = json.load(m)

    os.makedirs("reassembled", exist_ok=True)
    output_path = os.path.join("reassembled", manifest["filename"])

    # 2. Vérification de l'existence de TOUS les chunks avant de commencer l'écriture
    # C'est la sécurité supplémentaire pour éviter de créer un fichier partiel
    for chunk_info in manifest["chunks"]:
        chunk_path = os.path.join("chunks", chunk_info["name"])
        if not os.path.exists(chunk_path):
            print("❌ Fichier introuvable.")
            return # Arrête tout ici, le message de succès ne sera pas lu

    # 3. Réassemblage réel
    with open(output_path, "wb") as output_file:
        for chunk_info in manifest["chunks"]:
            chunk_path = os.path.join("chunks", chunk_info["name"])
            
            with open(chunk_path, "rb") as chunk_file:
                data = chunk_file.read()

                if calculate_hash(data) != chunk_info["hash"]:
                    print(f"❌ Erreur : Hash incorrect pour {chunk_info['name']}")
                    return

                output_file.write(data)

    # Ce message est hors de la boucle et après les vérifications
    print(f"✅ Fichier '{manifest['filename']}' réassemblé avec succès !")

if __name__ == "__main__":
    file_name = input("Entrez le nom exact du fichier à découper : ")
    split_file(file_name)
    reassemble_file()