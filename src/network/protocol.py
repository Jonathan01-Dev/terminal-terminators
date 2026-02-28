# ==========================================
# TYPES DE MESSAGES ARCHIPEL (Full Compatibility)
# ==========================================

# 1. Handshake & Sécurité
MSG_HELLO           = 0x00
MSG_PUB_KEY         = 0x01
MSG_SESSION_KEY     = 0x02
MSG_HANDSHAKE_READY = 0x06  # <--- C'est celle-ci qui te manquait !

# 2. Transfert de Fichiers
MSG_FILE_CHUNK      = 0x03
MSG_MANIFEST        = 0x04

# 3. Messagerie
MSG_CHAT_TEXT       = 0x05

# --- ALIAS DE COMPATIBILITÉ (Au cas où) ---
MSG_KEY_EXCHANGE    = MSG_SESSION_KEY

# ==========================================
# FONCTIONS DE TRANSPORT TLV
# ==========================================

def format_tlv(m_type, value):
    """Encapsule : [Type:1 octet][Length:4 octets][Value]"""
    length = len(value)
    return m_type.to_bytes(1, 'big') + length.to_bytes(4, 'big') + value

def receive_tlv(sock):
    """Lit un message complet au format TLV"""
    try:
        # Lecture du Type
        type_data = sock.recv(1)
        if not type_data: return None, None
        m_type = int.from_bytes(type_data, 'big')
        
        # Lecture de la Longueur
        len_data = sock.recv(4)
        if not len_data: return None, None
        length = int.from_bytes(len_data, 'big')
        
        # Lecture de la Valeur
        value = b''
        while len(value) < length:
            chunk = sock.recv(min(length - len(value), 4096))
            if not chunk: break
            value += chunk
            
        return m_type, value
    except Exception:
        return None, None