#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
NETWORK_DIR="${ROOT_DIR}/network/besu"
OUT_DIR="${NETWORK_DIR}/deployments/${CHAIN_ID:-20260720}"
RPC_URL="${RPC_URL:-http://127.0.0.1:${RPC_HTTP_PORT:-8545}}"

required=(CHAIN_ID DEPLOYER_PRIVATE_KEY ADMIN_PRIVATE_KEY REGISTRY_ADMIN_ADDRESS WRITER_ADDRESS)
for name in "${required[@]}"; do
  [[ -n "${!name:-}" ]] || { echo "missing required env: $name" >&2; exit 1; }
done

python "${NETWORK_DIR}/scripts/wait-for-rpc.py" --rpc-url "$RPC_URL" --timeout-seconds 120
actual_chain_id="$(cast chain-id --rpc-url "$RPC_URL")"
[[ "$actual_chain_id" == "$CHAIN_ID" ]] || {
  echo "chain ID mismatch: expected $CHAIN_ID got $actual_chain_id" >&2
  exit 1
}

forge build
forge script script/DeployEvidenceRegistry.s.sol:DeployEvidenceRegistry \
  --rpc-url "$RPC_URL" \
  --broadcast \
  -vvvv

latest_run="$(find "${ROOT_DIR}/broadcast/DeployEvidenceRegistry.s.sol/${CHAIN_ID}" -name run-latest.json -print -quit)"
contract_address="$(python - "$latest_run" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
for tx in payload.get("transactions", []):
    if tx.get("contractName") == "EvidenceRegistry" and tx.get("contractAddress"):
        print(tx["contractAddress"])
        break
PY
)"
[[ -n "$contract_address" ]] || { echo "failed to read deployed contract address" >&2; exit 1; }

export CONTRACT_ADDRESS="$contract_address"
forge script script/GrantWriterRole.s.sol:GrantWriterRole --rpc-url "$RPC_URL" --broadcast -vvvv
if [[ -n "${PAUSER_ADDRESS:-}" ]]; then
  forge script script/GrantPauserRole.s.sol:GrantPauserRole --rpc-url "$RPC_URL" --broadcast -vvvv
fi

mkdir -p "$OUT_DIR"
python scripts/generate_deployment_manifest.py \
  --network "besu-qbft" \
  --rpc-url "$RPC_URL" \
  --chain-id "$CHAIN_ID" \
  --contract-address "$CONTRACT_ADDRESS" \
  --deployer-address "$(cast wallet address --private-key "$DEPLOYER_PRIVATE_KEY")" \
  --admin-address "$REGISTRY_ADMIN_ADDRESS" \
  --output "${OUT_DIR}/EvidenceRegistry.json"
python scripts/verify_deployment.py --manifest "${OUT_DIR}/EvidenceRegistry.json"
printf "CONTRACT_ADDRESS=%s\n" "$CONTRACT_ADDRESS" > "${OUT_DIR}/contract-address.env"
echo "[PASS] deployed EvidenceRegistry: $CONTRACT_ADDRESS"
