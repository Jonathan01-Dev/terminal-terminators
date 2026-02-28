# Guide de Déploiement : ARCHIPEL sur Machines Physiques

Ce document explique comment lancer le projet Archipel sur plusieurs machines connectées au même réseau (ex: même réseau WiFi ou LAN) pour valider le Hackathon.

## Prérequis

1. Toutes les machines doivent être connectées au **même réseau local (WiFi ou câble)**.
2. Le pare-feu (Windows Defender, UFW, etc.) doit autoriser :
   - Le trafic UDP sur le port **6000** (pour la découverte `Multicast`).
   - Le trafic TCP sur le port choisi pour le nœud (ex: **5060**).
3. **Python 3.8+** doit être installé.

## Installation (Sur chaque machine)

1. Clonez ou copiez le dossier `ARCHIPEL_PROJECT` sur la machine.
2. Ouvrez un terminal dans le dossier du projet.
3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Exécution de Démonstration

### 1. Activer les Nœuds

Sur chaque machine, ouvrez un terminal et lancez le nœud Archipel. Par défaut, le port 5060 est utilisé.

**Machine A (Alice) :**
```bash
python main.py start --port 5060 --folder shared_files
```
*Le dossier `shared_files` sera créé automatiquement s'il n'existe pas.*

**Machine B (Bob) :**
```bash
python main.py start --port 5060 --folder shared_files
```

**Machine C (Charlie) :**
```bash
python main.py start --port 5060 --folder shared_files
```

> **Note :** Si vous testez plusieurs nœuds sur la *même* machine pour simuler le réseau, vous devez obligatoirement utiliser des ports différents (ex: 5060, 5061, 5062) et des dossiers différents (`--folder shared_files_bob`).

### 2. Vérifier la Découverte (UDP Multicast)

Laissez le premier terminal tourner en arrière-plan (serveur P2P).
Sur n'importe quelle machine (ex: Machine A), ouvrez un **deuxième terminal**, toujours dans le dossier `ARCHIPEL_PROJECT`.

Vérifiez que les autres machines sont visibles :
```bash
python main.py peers
```
*Vous devriez voir les IP et Ports des machines B et C s'afficher dans un tableau.*

### 3. Envoyer un Message Chiffré

Depuis le terminal de contrôle de la Machine A, envoyez un message à la Machine B (remplacez `IP_DE_BOB` par l'adresse IP affichée dans le tableau précédent, ex: `192.168.1.45:5060`).

```bash
python main.py msg IP_DE_BOB:5060 "Salut Bob, ça marche !"
```
*Regardez le premier terminal de la Machine B : le message déchiffré devrait s'afficher.*

### 4. Transférer un Fichier

Placez un fichier de test (ex: `document.pdf`) à la racine du projet `ARCHIPEL_PROJECT` sur la Machine A.

Envoyez-le vers la Machine B :
```bash
python main.py send IP_DE_BOB:5060 document.pdf
```
*Vérifiez le dossier `shared_files` de la Machine B : le fichier `document.pdf` s'y trouve, transféré de façon chiffrée.*

### 5. Approuver un Pair (Trust On First Use)

Si vous voulez ajouter la Machine B à votre liste de confiance :
```bash
python main.py trust ARCH-NOMDELAMACHINE
```
*Le statut passera à ⭐ TRUSTED lors du prochain `python main.py status`.*

## Résolution des Problèmes (Troubleshooting)

- **Je ne vois pas les autres nœuds avec `peers`** : Désactivez temporairement le pare-feu Windows/Linux ou ajoutez une règle autorisant `python.exe` sur le réseau privé. Le Multicast (UDP 224.0.0.1) est souvent bloqué par défaut.
- **Erreur "Format IP:PORT requis"** : Assurez-vous d'utiliser l'adresse IP exacte sans espaces (ex: `192.168.1.15:5060`).
