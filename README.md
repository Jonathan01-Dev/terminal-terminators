# 🌊 Projet Archipel - Équipe Terminal Terminators

## 🛠 Choix Techniques
* **Langage :** **Python 3.x**
    * *Pourquoi ?* Pour sa simplicité de gestion des sockets, sa rapidité de développement et ses bibliothèques cryptographiques (PyNaCl) robustes.
* **Communication Réseau :**
    * **UDP Multicast :** Utilisé pour la découverte automatique des pairs sur le réseau local (IP: 239.255.42.42).
    * **TCP :** (À venir) Utilisé pour le transfert de fichiers sécurisé.
* **Sécurité :** Chiffrement AES et signatures Ed25519.

## 🚀 Fonctionnalités actuelles (Sprint 0)
- [x] Configuration de l'environnement (Git, .env, .gitignore).
- [x] Script de découverte automatique via UDP Multicast.
- [x] Gestion dynamique de la table des pairs (Peers).

## ⚙️ Installation
1. Installer les dépendances :
   ```bash
   pip install pynacl pycryptodome python-dotenv


   ==================== ARCHITECTURE ====================

Chaque noeud du réseau exécute :

- Un client UDP (envoi HELLO)
- Un listener UDP (réception HELLO)
- Une Peer Table (stockage des voisins)
- Un serveur TCP (réception fichiers)

-------------------------------------------------------

               UDP Multicast 239.255.42.42:4242
        ------------------------------------------------
        |                  |                  |
     [Node 1]           [Node 2]           [Node 3]
        |                  |                  |
        ------------------------------------------------

TCP Communication (Peer to Peer)
--------------------------------------------------------
Node 1  <-------------------->  Node 2   (Port 5000)
Node 2  <-------------------->  Node 3   (Port 5000)
Node 1  <-------------------->  Node 3   (Port 5000)

========================================================
