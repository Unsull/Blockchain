from __future__ import annotations

import argparse
import ipaddress
import json
import os
import re
from pathlib import Path

SERVICES = ["validator-1", "validator-2", "validator-3", "validator-4"]
PUBLIC_KEY_PATTERN = re.compile(r"[0-9a-fA-F]{128}")


def read_public_key(path: Path) -> str:
    key = path.read_text(encoding="utf-8").strip()
    if key.startswith("0x"):
        key = key[2:]
    if not PUBLIC_KEY_PATTERN.fullmatch(key):
        raise SystemExit(f"invalid public key in {path}: expected 128 hexadecimal characters")
    return key.lower()


def read_ip(service: str, cli_value: str | None) -> str:
    env_name = service.replace("-", "_").upper() + "_IP"
    value = cli_value or os.environ.get(env_name)
    if not value:
        raise SystemExit(f"missing {env_name}")
    try:
        address = ipaddress.ip_address(value)
    except ValueError as error:
        raise SystemExit(f"invalid {env_name}: {value}") from error
    if address.version != 4:
        raise SystemExit(f"{env_name} must be an IPv4 address")
    return str(address)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render Besu static-nodes.json from generated keys."
    )
    parser.add_argument("--keys-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    for service in SERVICES:
        parser.add_argument(f"--{service}-ip")
    args = parser.parse_args()

    enodes: list[str] = []
    public_keys: set[str] = set()
    endpoints: set[tuple[str, int]] = set()
    for service in SERVICES:
        public_key = read_public_key(args.keys_dir / service / "key.pub")
        ip = read_ip(service, getattr(args, service.replace("-", "_") + "_ip"))
        endpoint = (ip, 30303)
        if public_key in public_keys:
            raise SystemExit(f"duplicate public key for {service}")
        if endpoint in endpoints:
            raise SystemExit(f"duplicate endpoint for {service}: {ip}:30303")
        public_keys.add(public_key)
        endpoints.add(endpoint)
        enodes.append(f"enode://{public_key}@{ip}:30303")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(enodes, indent=2) + "\n", encoding="utf-8")
    print(f"[PASS] static peer count: {len(enodes)}")


if __name__ == "__main__":
    main()
