# Archipel P2P

Hackathon project: A decentralized, encrypted peer-to-peer file transfer and messaging application.

## Architecture

```text
 +----------------+       +----------------+       +----------------+
 |    Node A      |       |    Node B      |       |    Node C      |
 | (CLI/Core/UI)  |<----->| (CLI/Core/UI)  |<----->| (CLI/Core/UI)  |
 +----------------+       +----------------+       +----------------+
        ^                                                 ^
        |                 TCP (Chiffré E2E)               |
        +-------------------------------------------------+
                          UDP Multicast
```

### Components
- **CLI**: Orchestrates user interactions.
- **Network**: Handles UDP Multicast discovery and TCP P2P connections.
- **Crypto**: Handles Ed25519 identity keys, X25519 session keys, and AES-256-GCM encryption.
- **Transfer**: File chunking, manifest generation, and downloading logic.
