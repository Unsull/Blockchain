#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"
FORCE=0

for arg in "$@"; do
  case "$arg" in
    --force) FORCE=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done

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

BESU_IMAGE="${BESU_IMAGE:-hyperledger/besu:${BESU_VERSION:-26.7.0}}"
BUILD_DIR="${ROOT_DIR}/build"
KEYS_DIR="${ROOT_DIR}/keys"
GENESIS_OUT="${ROOT_DIR}/genesis/genesis.json"
CONFIG_FILE="${ROOT_DIR}/genesis/qbftConfigFile.json"

to_docker_path() {
  local path="$1"
  if [[ -n "${MSYSTEM:-}" ]] && command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$path" | sed 's#\\#/#g'
  else
    printf '%s' "$path"
  fi
}

docker_run() {
  MSYS_NO_PATHCONV=1 docker run "$@"
}

command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 1; }
[[ -f "$CONFIG_FILE" ]] || { echo "missing $CONFIG_FILE" >&2; exit 1; }

if [[ -e "$BUILD_DIR" || -e "$KEYS_DIR" || -e "$GENESIS_OUT" ]]; then
  if [[ "$FORCE" != "1" ]]; then
    echo "generated network output already exists; rerun with --force" >&2
    exit 1
  fi
  rm -rf "$BUILD_DIR" "$KEYS_DIR" "$GENESIS_OUT"
fi

mkdir -p "$BUILD_DIR" "$KEYS_DIR"
docker image inspect "$BESU_IMAGE" >/dev/null 2>&1 || docker pull "$BESU_IMAGE"

GENESIS_MOUNT="$(to_docker_path "${ROOT_DIR}/genesis")"
BUILD_MOUNT="$(to_docker_path "$BUILD_DIR")"
KEYS_MOUNT="$(to_docker_path "$KEYS_DIR")"

docker_run --rm \
  -u "$(id -u):$(id -g)" \
  -v "${GENESIS_MOUNT}:/config" \
  -v "${BUILD_MOUNT}:/output" \
  "$BESU_IMAGE" operator generate-blockchain-config \
  --config-file=/config/qbftConfigFile.json \
  --to=/output \
  --private-key-file-name=key

cp "${BUILD_DIR}/genesis.json" "$GENESIS_OUT"

mapfile -t NODE_DIRS < <(find "$BUILD_DIR/keys" -mindepth 1 -maxdepth 1 -type d | sort)
if [[ "${#NODE_DIRS[@]}" -ne 4 ]]; then
  echo "expected 4 generated validator keys, got ${#NODE_DIRS[@]}" >&2
  exit 1
fi

for index in 1 2 3 4; do
  src="${NODE_DIRS[$((index - 1))]}"
  dest="${KEYS_DIR}/validator-${index}"
  mkdir -p "$dest"
  install -m 0400 "${src}/key" "${dest}/key"
  cp "${src}/key.pub" "${dest}/key.pub"
  if [[ -f "${src}/address" ]]; then
    cp "${src}/address" "${dest}/address"
  fi
done

mkdir -p "${KEYS_DIR}/rpc-node"
python - <<'PY' > "${KEYS_DIR}/rpc-node/key"
import secrets
print(secrets.token_hex(32))
PY
chmod 0400 "${KEYS_DIR}/rpc-node/key"
docker_run --rm \
  -u "$(id -u):$(id -g)" \
  -v "${KEYS_MOUNT}:/keys" \
  "$BESU_IMAGE" public-key export-address \
  --node-private-key-file=/keys/rpc-node/key \
  --to=/keys/rpc-node/address >/dev/null

python "${ROOT_DIR}/scripts/render-static-nodes.py" \
  --keys-dir "$KEYS_DIR" \
  --output "${BUILD_DIR}/static-nodes.json"

python "${ROOT_DIR}/scripts/validate-generated-network.py" \
  --root "$ROOT_DIR" \
  --expected-validators 4

echo "[PASS] generated genesis: ${GENESIS_OUT}"
echo "[PASS] generated static peers: ${BUILD_DIR}/static-nodes.json"
echo "[PASS] validator public metadata written under ${KEYS_DIR}"
