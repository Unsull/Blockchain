# Private Network Guidance

This directory contains private network material for integrating the blockchain
module with a private EVM network. The current integration/staging stack is
`network/besu`, which uses Hyperledger Besu `26.7.0`, QBFT, four validators, and
one separate RPC node.

Legacy example files in this directory remain reference-only. Use
`network/besu/README.md` for the maintained Docker Compose workflow.

## Topology

- Validator nodes for consensus.
- RPC node dedicated to backend traffic.
- Persistent volumes for chain data.
- Monitoring and alerting for peers, block production, disk, and RPC health.
- Backup procedure for node keys and chain data.
- Firewall and RPC allowlist.
- TLS or a reverse proxy for backend-to-RPC traffic.

## Besu QBFT Quick Start

```bash
cd network/besu
cp .env.example .env
scripts/generate-network.sh --force
scripts/start-network.sh
```

RPC binds to `127.0.0.1:${RPC_HTTP_PORT}` and exposes only `eth`, `net`, and
`web3`.

## RPC Namespaces

Expose to backend:

- `eth`
- `net`
- `web3`

Do not expose:

- `personal`
- `admin`
- `debug`
- `miner`
