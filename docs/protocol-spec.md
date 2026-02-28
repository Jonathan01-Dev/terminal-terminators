# P2P Protocol Specification

## 1. Overview

This document describes the binary protocol used for:

- Peer discovery (UDP Multicast)
- File transfer (TCP)

The architecture is fully peer-to-peer (P2P).  
Each node can send and receive messages.

All messages follow a structured binary format.

---

## 2. General Packet Structure

Each packet uses the following binary format:

+------------+------------+--------------+------------------+
| Version(1) | Type(1)    | Length(4)    | Payload(variable)|
+------------+------------+--------------+------------------+

Total header size: 6 bytes

---

## 3. Field Description

### 3.1 Version (1 byte)

Protocol version number.

Current version:
- `0x01`

This allows future protocol upgrades.

---

### 3.2 Type (1 byte)

Defines the message type.

| Value | Meaning |
|--------|----------|
| 0x01 | HELLO |
| 0x02 | FILE_CHUNK |
| 0x03 | FILE_REQUEST |
| 0x04 | FILE_END |

---

### 3.3 Length (4 bytes)

Unsigned 32-bit integer (Big Endian).

Indicates the size of the payload in bytes.

Example:
If payload is 100 bytes → Length = 0x00000064

---

### 3.4 Payload (variable)

Contains the actual message data.

Examples:

- For HELLO:
  Payload may contain:
  - Peer ID
  - TCP listening port

- For FILE_CHUNK:
  Payload contains:
  - Binary data of file chunk

---

## 4. UDP Discovery Message

Transport: UDP Multicast  
Address: 239.255.42.42  
Port: 4242  

Type used:
- `0x01` (HELLO)

Payload example:
- Node ID (string)
- TCP listening port (2 bytes)

---

## 5. TCP File Transfer

Transport: TCP  
Port: 5000  

Used message types:

- `0x02` → FILE_CHUNK
- `0x03` → FILE_REQUEST
- `0x04` → FILE_END

File transfer process:

1. Client sends FILE_REQUEST
2. Server responds with FILE_CHUNK packets
3. Transfer ends with FILE_END

---

## 6. Endianness

All multi-byte integers are encoded using:

Big Endian (network byte order)

---

## 7. Future Improvements

- Message authentication
- Encryption (TLS)
- Compression
- Chunk checksum validation

---

## 8. Design Philosophy

- Lightweight
- Simple header
- Easily extensible
- Compatible with P2P architecture
