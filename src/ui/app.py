import os
import threading
from flask import Flask, render_template, request, jsonify
from src.network.discovery import start_discovery, get_formatted_peers_data
from src.network.server_p2p import start_node
from src.network.client import send_secure_msg, send_file_secure
from src.security.trust_manager import is_trusted, add_to_trust
import socket

# Init Flask
app = Flask(__name__)
node_started = False
NODE_PORT = 5060

def start_background_node(port, folder):
    global node_started
    if not node_started:
        print("Starting background P2P node...")
        # Start UDP Discovery
        start_discovery(port)
        # Start TCP Server
        threading.Thread(target=start_node, args=(port, folder), daemon=True).start()
        node_started = True

@app.route("/")
def index():
    """Rend la page principale (Dashboard)"""
    return render_template("index.html")

@app.route("/api/start", methods=["POST"])
def api_start():
    """Démarre le noeud en arrière-plan"""
    global node_started
    if node_started:
        return jsonify({"status": "already_running"}), 200
    
    port = request.json.get("port", NODE_PORT)
    folder = request.json.get("folder", "shared_files")
    
    start_background_node(port, folder)
    return jsonify({"status": "started", "port": port, "folder": folder})

@app.route("/api/status", methods=["GET"])
def api_status():
    """Renvoie le statut global et l'identité locale"""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    node_id = f"ARCH-{hostname.upper()}"
    
    return jsonify({
        "status": "online" if node_started else "offline",
        "node_id": node_id,
        "local_ip": local_ip,
        "port": NODE_PORT
    })

@app.route("/api/peers", methods=["GET"])
def api_peers():
    """Renvoie la liste des pairs au format JSON"""
    if not node_started:
        return jsonify([])
        
    peers_data = get_formatted_peers_data()
    # Mappage pour l'API
    result = []
    for p in peers_data:
        # [peer_id, status_html, delay_str, crypto_str]
        status_clean = "Online" if "Online" in p[1] else "Offline"
        result.append({
            "id": p[0],
            "ip_port": p[0],
            "status": status_clean,
            "last_seen": p[2],
            "trusted": is_trusted(p[0])
        })
    return jsonify(result)

@app.route("/api/trust", methods=["POST"])
def api_trust():
    """Rend un noeud 'Trusted'"""
    node_id = request.json.get("node_id")
    if not node_id:
        return jsonify({"error": "Missing node_id"}), 400
        
    success = add_to_trust(node_id)
    return jsonify({"status": "trusted" if success else "already_trusted"})

@app.route("/api/message", methods=["POST"])
def api_message():
    """Envoie un message à un pair"""
    target = request.json.get("target")
    content = request.json.get("content")
    
    if not target or not content:
        return jsonify({"error": "Missing target or content"}), 400
        
    ip, port = target.split(":")
    result = send_secure_msg(ip, port, content)
    return jsonify({"result": result})

@app.route("/api/sendfile", methods=["POST"])
def api_sendfile():
    """Envoie un fichier à un pair"""
    target = request.json.get("target")
    filepath = request.json.get("filepath")
    
    if not target or not filepath:
        return jsonify({"error": "Missing target or filepath"}), 400
        
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found locally"}), 404
        
    ip, port = target.split(":")
    result = send_file_secure(ip, port, filepath)
    return jsonify({"result": result})

def run_flask(port=8080):
    """Lance le dashboard Flask"""
    print(f"🌍 Web Dashboard running on http://127.0.0.1:{port}")
    # Desactive le hot reload pour ne pas relancer le noeud P2P bêtement
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == "__main__":
    run_flask()
