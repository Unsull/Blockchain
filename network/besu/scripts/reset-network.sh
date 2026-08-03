#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIRM=0
REGENERATE_KEYS=0
for arg in "$@"; do
  case "$arg" in
    --confirm|--force) CONFIRM=1 ;;
    --regenerate-keys) REGENERATE_KEYS=1 ;;
    *) echo "unknown argument: $arg" >&2; exit 2 ;;
  esac
done
[[ "$CONFIRM" == "1" ]] || { echo "refusing to delete chain data without --confirm" >&2; exit 1; }
docker compose --project-directory "$ROOT_DIR" down -v
rm -rf "${ROOT_DIR}/nodes/"*/data/*
find "${ROOT_DIR}/nodes" -path "*/data" -type d -exec sh -c 'touch "$1/.gitkeep"' sh {} \;
if [[ "$REGENERATE_KEYS" == "1" ]]; then
  rm -rf "${ROOT_DIR}/build" "${ROOT_DIR}/keys" "${ROOT_DIR}/genesis/generated"
  echo "[WARN] validator identities removed; run generate-network.sh --force"
else
  rm -rf "${ROOT_DIR}/logs"
fi
