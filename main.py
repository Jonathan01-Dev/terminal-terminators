import argparse
import sys
import os
import socket
from tabulate import tabulate
from colorama import Fore, Style, init

# Initialisation des couleurs pour le terminal (Windows/Linux/macOS)
init(autoreset=True)

# Ajout du dossier racine au système pour les imports internes
sys.path.append(os.getcwd())

def main():
    # --- 1. CONFIGURATION DES ARGUMENTS (CLI STRUCTURE) ---
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}🛡️ ARCHIPEL - Système P2P Sécurisé (Sprint 4){Style.RESET_ALL}",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Option globale pour désactiver l'IA ou forcer le mode hors-ligne
    parser.add_argument("--no-ai", action="store_true", help="Désactiver l'assistance IA (Mode local)")

    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Commande : START
    start_p = subparsers.add_parser("start", help="Lancer le nœud ARCHIPEL local")
    start_p.add_argument("--port", type=int, default=5060, help="Port TCP (défaut: 5060)")
    start_p.add_argument("--folder", default="shared_files", help="Dossier de stockage")

    # Commande : PEERS
    subparsers.add_parser("peers", help="Lister les pairs actifs sur le réseau")

    # Commande : ASK (Assistant IA Gemini)
    ask_p = subparsers.add_parser("ask", help="Poser une question technique à l'assistant IA")
    ask_p.add_argument("query", nargs="+", help="Votre question (ex: 'C'est quoi le RSA ?')")

    # Commande : MSG
    msg_p = subparsers.add_parser("msg", help="Envoyer un message chiffré")
    msg_p.add_argument("target", help="Cible IP:PORT (ex: 127.0.0.1:5060)")
    msg_p.add_argument("content", help="Contenu du message")

    # Commande : SEND
    send_p = subparsers.add_parser("send", help="Envoyer un fichier segmenté")
    send_p.add_argument("target", help="Cible IP:PORT")
    send_p.add_argument("file", help="Chemin du fichier local")

    # Commande : TRUST
    trust_p = subparsers.add_parser("trust", help="Approuver un pair dans le cercle de confiance")
    trust_p.add_argument("node_id", help="L'ID du nœud à approuver (ex: ARCH-PC1)")

    # Commande : STATUS
    subparsers.add_parser("status", help="Afficher l'état du système et le tableau de bord")

    # --- 2. ANALYSE DES ARGUMENTS ---
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # --- 3. LOGIQUE D'EXÉCUTION ---
    
    # 🚀 START : Lancement du serveur et de la découverte
    if args.command == "start":
        from src.network.discovery import start_discovery
        from src.network.server_p2p import start_node
        print(f"{Fore.CYAN}🚀 Initialisation du nœud ARCHIPEL...")
        print(f"📍 Port : {args.port} | 📁 Dossier : {args.folder}")
        start_discovery(args.port)
        start_node(args.port, args.folder)

    # 📋 PEERS : Liste les pairs détectés en UDP
    elif args.command == "peers":
        from src.network.discovery import get_formatted_peers_data
        data = get_formatted_peers_data()
        print(f"\n{Fore.WHITE}{Style.BRIGHT}📋 TABLE DES PAIRS DÉCOUVERTS")
        if not data:
            print(f"{Fore.YELLOW}🔎 Aucun pair détecté sur le réseau local.")
        else:
            headers = ["Node (IP:Port)", "Status", "Last Seen", "Security"]
            print(tabulate(data, headers=headers, tablefmt="grid"))

    # 🤖 ASK : Assistant IA Gemini avec Fallback
    elif args.command == "ask":
        try:
            from src.ai.gemini import ArchipelAI
            assistant = ArchipelAI(no_ai_flag=args.no_ai)
            user_query = " ".join(args.query)
            print(f"\n{Fore.BLUE}🤔 Analyse de la question...{Style.RESET_ALL}")
            print(assistant.ask(user_query))
        except ModuleNotFoundError:
            print(f"{Fore.RED}❌ Erreur : Installez l'IA avec 'pip install -U google-generativeai'")

    # 💬 MSG : Envoi de message avec Handshake RSA/AES
    elif args.command == "msg":
        if ":" in args.target:
            ip, port = args.target.split(":")
            from src.network.client import send_secure_msg
            print(f"{Fore.BLUE}🔒 Sécurisation du message pour {args.target}...")
            result = send_secure_msg(ip, port, args.content)
            print(result)
        else:
            print(f"{Fore.RED}❌ Erreur : Format IP:PORT requis.")

    # 📦 SEND : Transfert de fichier sécurisé
    elif args.command == "send":
        if ":" in args.target:
            ip, port = args.target.split(":")
            from src.network.client import send_file_secure
            if os.path.exists(args.file):
                print(f"{Fore.BLUE}📦 Préparation de l'envoi : {args.file}")
                result = send_file_secure(ip, port, args.file)
                print(result)
            else:
                print(f"{Fore.RED}❌ Fichier introuvable : {args.file}")
        else:
            print(f"{Fore.RED}❌ Erreur : Format IP:PORT requis.")

    # ⭐ TRUST : Gestion de la liste blanche
    elif args.command == "trust":
        from src.security.trust_manager import add_to_trust
        if add_to_trust(args.node_id):
            print(f"{Fore.GREEN}✅ Le nœud {args.node_id} est maintenant APPROUVÉ.")
        else:
            print(f"{Fore.YELLOW}ℹ️ Le nœud {args.node_id} est déjà dans la liste de confiance.")

    # 📊 STATUS : Dashboard complet
    elif args.command == "status":
        from src.network.discovery import get_formatted_peers_data
        from src.security.trust_manager import is_trusted
        
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        node_id = f"ARCH-{hostname.upper()}"
        
        peers_data = get_formatted_peers_data()
        nb_peers = len(peers_data) if peers_data else 0
        shared_folder = "shared_files"
        files = os.listdir(shared_folder) if os.path.exists(shared_folder) else []

        print(f"\n{Fore.CYAN}📊 ARCHIPEL - TABLEAU DE BORD")
        print(f"{Fore.WHITE}{'='*50}")
        print(f"{Fore.YELLOW}🆔 IDENTITÉ LOCALE")
        print(f"   • ID Node  : {Fore.GREEN}{node_id}")
        print(f"   • IP Adr   : {Fore.GREEN}{local_ip}")
        print(f"   • Statut   : {Fore.GREEN}Opérationnel (Sprint 4)")
        
        print(f"\n{Fore.YELLOW}🌐 RÉSEAU P2P")
        print(f"   • Pairs connectés : {Fore.MAGENTA}{nb_peers}")
        if nb_peers > 0:
            for peer in peers_data:
                trust_status = "⭐ TRUSTED" if is_trusted(peer[0]) else "❌ UNTRUSTED"
                print(f"     - {peer[0]} | {trust_status}")
        
        print(f"\n{Fore.YELLOW}📂 DOSSIER PARTAGÉ ({shared_folder})")
        if not files:
            print(f"   • {Fore.RED}Aucun fichier disponible.")
        else:
            print(f"   • Fichiers prêts ({len(files)}) :")
            for f in files:
                size = os.path.getsize(os.path.join(shared_folder, f)) / 1024
                print(f"     - {f} ({size:.1f} KB)")
        print(f"{Fore.WHITE}{'='*50}\n")

if __name__ == "__main__":
    main()