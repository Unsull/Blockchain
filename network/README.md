# Private Network Guidance

This directory contains example-only private network material for integrating
the blockchain module with a private EVM network.

Pin the Geth version in deployment documentation before production use. The
templates here are not a claim of multi-node production readiness; validate them
against the exact Geth release and consensus mode used by the deployment.

## Topology

- Validator nodes for consensus.
- RPC node dedicated to backend traffic.
- Persistent volumes for chain data.
- Monitoring and alerting for peers, block production, disk, and RPC health.
- Backup procedure for node keys and chain data.
- Firewall and RPC allowlist.
- TLS or a reverse proxy for backend-to-RPC traffic.

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
