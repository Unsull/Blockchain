#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
elif [[ -f "${ROOT_DIR}/.env.example" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ROOT_DIR}/.env.example"
  set +a
fi
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
  --expected-chain-id "${CHAIN_ID:-20260720}" \
  --min-peers "${MIN_PEERS:-3}" \
  --block-wait-seconds "${BLOCK_WAIT_SECONDS:-15}"
docker compose --project-directory "$ROOT_DIR" ps
