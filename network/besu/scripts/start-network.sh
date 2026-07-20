#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[[ -f "${ROOT_DIR}/genesis/genesis.json" ]] || {
  echo "generated network missing; run scripts/generate-network.sh first" >&2
  exit 1
}
docker compose --project-directory "$ROOT_DIR" up -d
python "${ROOT_DIR}/scripts/wait-for-rpc.py" \
  --rpc-url "http://127.0.0.1:${RPC_HTTP_PORT:-8545}" \
  --timeout-seconds 120
python "${ROOT_DIR}/scripts/health-check.py" \
  --rpc-url "http://127.0.0.1:${RPC_HTTP_PORT:-8545}" \
  --expected-chain-id "${CHAIN_ID:-20260720}"
docker compose --project-directory "$ROOT_DIR" ps
