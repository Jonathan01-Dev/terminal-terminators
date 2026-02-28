import google.generativeai as genai
from colorama import Fore, Style

# Clé API intégrée directement pour la démo
GEMINI_API_KEY = "AIzaSyCdpgw7QOarLxYjqVtJ8ATqzelfLrdu9a0"

class ArchipelAI:
    def __init__(self, no_ai_flag=False):
        """
        Initialise l'assistant Gemini avec fallback automatique.
        :param no_ai_flag: Si True, force le mode hors-ligne immédiatement.
        """
        self.offline_mode = no_ai_flag
        self.model = None
        
        if not self.offline_mode:
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Configuration du modèle Pro
                self.model = genai.GenerativeModel('gemini-pro')
                # Test rapide de connexion (optionnel mais recommandé)
            except Exception:
                self.offline_mode = True

    def ask(self, prompt):
        """Méthode principale pour poser une question à l'assistant"""
        if self.offline_mode or self.model is None:
            return self._get_local_fallback(prompt)

        try:
            # On ajoute un contexte système pour que l'IA sache de quoi on parle
            context = (
                "Tu es l'assistant du projet ARCHIPEL (Système P2P Sécurisé). "
                "Réponds de manière concise et technique. "
            )
            full_prompt = f"{context}\nUtilisateur: {prompt}"
            
            response = self.model.generate_content(full_prompt)
            return f"{Fore.CYAN}✨ Gemini:{Style.RESET_ALL} {response.text}"
            
        except Exception as e:
            # En cas de timeout ou erreur API, on bascule gracieusement
            return self._get_local_fallback(prompt)

    def _get_local_fallback(self, prompt):
        """Système de réponses locales si l'IA est inaccessible (Mode Hors-ligne)"""
        p = prompt.lower()
        
        # Base de connaissance locale simplifiée
        kb = {
            "rsa": "Le RSA-2048 est utilisé dans ARCHIPEL pour l'échange sécurisé de la clé de session AES.",
            "aes": "Nous utilisons l'AES-256-GCM pour chiffrer les messages et les fichiers de bout en bout.",
            "tlv": "Le protocole TLV (Type-Length-Value) structure nos paquets : [Type:1b][Len:4b][Value].",
            "p2p": "ARCHIPEL est décentralisé : chaque nœud est à la fois client et serveur.",
            "trust": "La commande 'trust' ajoute un Node ID dans trusted_peers.json pour filtrer les accès.",
            "aide": "Commandes disponibles : start, msg, send, status, peers, trust.",
            "erreur": "Vérifiez votre connexion internet ou le flag --no-ai."
        }

        # Recherche de correspondance dans le prompt
        for key, value in kb.items():
            if key in p:
                return f"{Fore.YELLOW}📂 [Local Fallback]:{Style.RESET_ALL} {value}"

        return f"{Fore.YELLOW}📂 [Local Fallback]:{Style.RESET_ALL} Mode hors-ligne actif. Posez une question sur RSA, AES, TLV ou tapez 'aide'."