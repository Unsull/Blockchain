#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
NETWORK_DIR="${ROOT_DIR}/network/besu"
ENV_FILE="${NETWORK_DIR}/.env"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi
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
forge script script/DeployEvidenceRegistryV3.s.sol:DeployEvidenceRegistryV3 \
  --rpc-url "$RPC_URL" \
  --broadcast \
  -vvvv

latest_run="${ROOT_DIR}/broadcast/DeployEvidenceRegistryV3.s.sol/${CHAIN_ID}/run-latest.json"
deployment_metadata="$(python - "$latest_run" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
for tx in payload.get("transactions", []):
    if tx.get("contractName") == "EvidenceRegistryV3" and tx.get("contractAddress"):
        receipt = next(
            item for item in payload.get("receipts", [])
            if item.get("transactionHash", "").lower() == tx.get("hash", "").lower()
        )
        print(tx["contractAddress"], tx["hash"], int(receipt["blockNumber"], 16))
        break
PY
)"
read -r contract_address deployment_transaction deployment_block <<< "$deployment_metadata"
[[ -n "$contract_address" ]] || { echo "failed to read deployed V3 contract address" >&2; exit 1; }

export CONTRACT_ADDRESS="$contract_address"
forge script script/GrantWriterRole.s.sol:GrantWriterRole --rpc-url "$RPC_URL" --broadcast -vvvv
grant_run="${ROOT_DIR}/broadcast/GrantWriterRole.s.sol/${CHAIN_ID}/run-latest.json"
grant_metadata="$(python - "$grant_run" <<'PY'
import json, sys
payload = json.load(open(sys.argv[1], encoding="utf-8"))
tx = payload["transactions"][0]
receipt = next(
    item for item in payload["receipts"]
    if item.get("transactionHash", "").lower() == tx.get("hash", "").lower()
)
print(tx["hash"], int(receipt["blockNumber"], 16))
PY
)"
read -r writer_grant_transaction writer_grant_block <<< "$grant_metadata"
if [[ -n "${PAUSER_ADDRESS:-}" ]]; then
  forge script script/GrantPauserRole.s.sol:GrantPauserRole --rpc-url "$RPC_URL" --broadcast -vvvv
fi

mkdir -p "$OUT_DIR"
python scripts/generate_deployment_manifest.py \
  --network "besu-qbft" \
  --rpc-url "$RPC_URL" \
  --chain-id "$CHAIN_ID" \
  --contract-name "EvidenceRegistryV3" \
  --contract-version "V3" \
  --contract-address "$CONTRACT_ADDRESS" \
  --deployer-address "$(cast wallet address --private-key "$DEPLOYER_PRIVATE_KEY")" \
  --admin-address "$REGISTRY_ADMIN_ADDRESS" \
  --writer-address "$WRITER_ADDRESS" \
  --deployment-transaction "$deployment_transaction" \
  --deployment-block "$deployment_block" \
  --writer-role-grant-transaction "$writer_grant_transaction" \
  --writer-role-grant-block "$writer_grant_block" \
  --output "${OUT_DIR}/EvidenceRegistryV3.json"
python scripts/verify_deployment.py --manifest "${OUT_DIR}/EvidenceRegistryV3.json"
printf "CONTRACT_ADDRESS=%s\n" "$CONTRACT_ADDRESS" > "${OUT_DIR}/contract-address.env"
echo "[PASS] deployed EvidenceRegistryV3: $CONTRACT_ADDRESS"
