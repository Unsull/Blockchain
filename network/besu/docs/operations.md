# Besu Operations

Generate:

```bash
cd network/besu
cp .env.example .env
scripts/generate-network.sh --force
```

To repair only static peer endpoints while preserving validator identities and
genesis, source the network environment and render from the existing keys:

```bash
set -a
source .env
set +a
python scripts/render-static-nodes.py --keys-dir keys --output build/static-nodes.json
python scripts/validate-generated-network.py --root . --expected-validators 4
```

For a new local or CI chain, fund public account addresses before the first
start. This command never accepts or writes private keys:

```bash
python scripts/fund-genesis.py --genesis genesis/genesis.json \
  --address 0xDEPLOYER_ADDRESS \
  --address 0xADMIN_ADDRESS
```

Do not change `genesis.json` after chain data has been initialized. Existing
data must continue to use the exact genesis from which it was created.

Start and stop:

```bash
scripts/start-network.sh
scripts/stop-network.sh
```

Status and logs:

```bash
docker compose ps
docker compose logs -f rpc-node
docker compose logs -f validator-1
```

Health:

```bash
python scripts/health-check.py --rpc-url http://127.0.0.1:8545 --expected-chain-id 20260720
```

Deploy registry:

```bash
RPC_URL=http://127.0.0.1:8545 CHAIN_ID=20260720 \
DEPLOYER_PRIVATE_KEY=... ADMIN_PRIVATE_KEY=... \
REGISTRY_ADMIN_ADDRESS=0x... WRITER_ADDRESS=0x... \
scripts/deploy-registry.sh
```

Troubleshooting:

- No peers: render static nodes from the existing public keys and confirm their
  IPs match the Compose network.
- Block not increasing: confirm at least three validators are online.
- Wrong chain ID: reset data and regenerate with the intended chain ID.
- RPC refused: check `rpc-node` health and localhost port binding.
- Validator key mismatch: restore the original key or rebuild the network.
- Genesis mismatch: all data must be reset; existing chain data cannot use a new
  genesis.
- Insufficient funds: add alloc before genesis generation or fund accounts from a
  funded account.
- Unauthorized role: grant `WRITER_ROLE`, `PAUSER_ROLE`, or admin role as needed.
- Missing contract address: read `network/besu/deployments/<chain_id>/contract-address.env`.
