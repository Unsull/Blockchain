# Besu QBFT Private Network

This directory defines an integration/staging private EVM network using
Hyperledger Besu `26.7.0`, QBFT consensus, Docker Compose, four validators, and
one separate RPC node.

The Docker image is pinned as `hyperledger/besu:26.7.0`; do not use `latest`.

## Quick Start

```bash
cd network/besu
cp .env.example .env
scripts/generate-network.sh --force
scripts/start-network.sh
```

RPC is available only on localhost:

```text
http://127.0.0.1:8545
```

## Topology

```text
validator-1  validator-2  validator-3  validator-4
     |            |            |            |
     +------------+------------+------------+
                  private QBFT P2P network
                              |
                           rpc-node
                              |
                backend / blockchain_client
```

Validators have RPC disabled. The RPC node exposes `ETH`, `NET`, and `WEB3`
only.

## Commands

```bash
docker compose config
python scripts/health-check.py --expected-chain-id 20260720
python scripts/smoke-test.py
python scripts/failure-test.py
scripts/deploy-registry.sh
```

See `docs/operations.md` for full workflows.

## Known Limitations

This stack is not a production claim. Complete backup drills, monitoring review,
security review, host deployment validation, and external signer validation
before production use.
