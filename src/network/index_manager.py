import json
import os

INDEX_FILE = ".archipel/index.json"

class IndexManager:
    @staticmethod
    def ensure_index():
        os.makedirs(".archipel", exist_ok=True)
        if not os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "w") as f:
                json.dump({}, f)

    @staticmethod
    def load_index():
        IndexManager.ensure_index()
        try:
            with open(INDEX_FILE, "r") as f:
                return json.load(f)
        except: return {}

    @staticmethod
    def register_file(file_hash, filename, local_path, size, status="complete"):
        index = IndexManager.load_index()
        index[file_hash] = {
            "filename": filename,
            "local_path": local_path,
            "size": size,
            "status": status,
            "chunks_available": list(range((size // 4096) + 1))
        }
        with open(INDEX_FILE, "w") as f:
            json.dump(index, f, indent=4)

    @staticmethod
    def get_file_path(file_hash):
        index = IndexManager.load_index()
        return index.get(file_hash, {}).get("local_path")