import struct

# Constantes de type
MSG_PING = 0
MSG_PONG = 1
MSG_TEXT = 2
MSG_FILE = 3

# --- Types de messages Handshake ---
MSG_HELLO = 4
MSG_PUB_KEY = 5
MSG_SESSION_KEY = 6
MSG_HANDSHAKE_READY = 7

def format_tlv(msg_type, data_bytes):
    """Prépare un paquet : [Type (1 octet)][Taille (4 octets)][Données]"""
    # !BI : Network Byte Order, 1 octet non signé, 4 octets non signés
    header = struct.pack('!BI', msg_type, len(data_bytes))
    return header + data_bytes

def receive_tlv(sock):
    """Lit un paquet TLV complet sur le réseau"""
    try:
        header = sock.recv(5)
        if not header or len(header) < 5:
            return None, None
        
        msg_type, length = struct.unpack('!BI', header)
        
        value = b''
        while len(value) < length:
            chunk = sock.recv(min(length - len(value), 4096))
            if not chunk: break
            value += chunk
        return msg_type, value
    except:
        return None, None