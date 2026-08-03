from __future__ import annotations

import argparse
import ipaddress
import json
import re
import subprocess
from pathlib import Path
from typing import Any

from eth_account import Account
from eth_utils import keccak

ENODE_PATTERN = re.compile(r"enode://([0-9a-fA-F]{128})@([^:]+):([0-9]{1,5})")


def decode_rlp(data: bytes, offset: int = 0) -> tuple[bytes | list[Any], int]:
    prefix = data[offset]
    if prefix <= 0x7F:
        return bytes([prefix]), offset + 1
    if prefix <= 0xB7:
        length = prefix - 0x80
        start = offset + 1
        return data[start : start + length], start + length
    if prefix <= 0xBF:
        length_size = prefix - 0xB7
        start = offset + 1
        length = int.from_bytes(data[start : start + length_size], "big")
        start += length_size
        return data[start : start + length], start + length
    if prefix <= 0xF7:
        length = prefix - 0xC0
        start = offset + 1
        end = start + length
    else:
        length_size = prefix - 0xF7
        start = offset + 1
        length = int.from_bytes(data[start : start + length_size], "big")
        start += length_size
        end = start + length
    items: list[Any] = []
    while start < end:
        item, start = decode_rlp(data, start)
        items.append(item)
    if start != end:
        raise ValueError("invalid RLP list length")
    return items, end


def validator_addresses(extra_data: str) -> set[str]:
    raw = bytes.fromhex(extra_data.removeprefix("0x"))
    decoded, end = decode_rlp(raw)
    if end != len(raw) or not isinstance(decoded, list) or len(decoded) < 2:
        raise SystemExit("invalid QBFT extraData")
    validators = decoded[1]
    if not isinstance(validators, list):
        raise SystemExit("invalid QBFT validator list")
    addresses = {
        value.hex() for value in validators if isinstance(value, bytes) and len(value) == 20
    }
    if len(addresses) != len(validators):
        raise SystemExit("invalid or duplicate validator address in QBFT extraData")
    return addresses


def compose_config(root: Path) -> dict[str, Any]:
    env_file = root / (".env" if (root / ".env").exists() else ".env.example")
    command = [
        "docker",
        "compose",
        "--project-directory",
        str(root),
        "--env-file",
        str(env_file),
        "config",
        "--format",
        "json",
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate generated Besu network artifacts.")
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--expected-validators", type=int, default=4)
    args = parser.parse_args()

    root = args.root.resolve()
    genesis_path = root / "genesis/genesis.json"
    static_nodes_path = root / "build/static-nodes.json"
    if not genesis_path.exists():
        raise SystemExit("missing generated genesis.json")
    if not static_nodes_path.exists():
        raise SystemExit("missing static-nodes.json")

    peers = json.loads(static_nodes_path.read_text(encoding="utf-8"))
    if not isinstance(peers, list) or len(peers) != args.expected_validators:
        raise SystemExit(f"expected {args.expected_validators} static peers")

    public_keys: set[str] = set()
    endpoints: set[tuple[str, int]] = set()
    key_addresses: set[str] = set()
    peer_ips: dict[str, str] = {}
    for index, enode in enumerate(peers, start=1):
        match = ENODE_PATTERN.fullmatch(enode) if isinstance(enode, str) else None
        if not match:
            raise SystemExit(f"invalid enode URL for validator-{index}: {enode}")
        public_key, ip_text, port_text = match.groups()
        try:
            ip = ipaddress.ip_address(ip_text)
        except ValueError as error:
            raise SystemExit(f"invalid enode IP for validator-{index}: {ip_text}") from error
        port = int(port_text)
        if ip.version != 4 or not 1 <= port <= 65535:
            raise SystemExit(f"invalid enode endpoint for validator-{index}")
        public_key = public_key.lower()
        endpoint = (str(ip), port)
        if public_key in public_keys:
            raise SystemExit(f"duplicate public key for validator-{index}")
        if endpoint in endpoints:
            raise SystemExit(f"duplicate endpoint for validator-{index}")

        key_path = root / f"keys/validator-{index}/key"
        public_key_path = root / f"keys/validator-{index}/key.pub"
        if not key_path.exists() or not public_key_path.exists():
            raise SystemExit(f"missing key material for validator-{index}")
        stored_public_key = (
            public_key_path.read_text(encoding="utf-8").strip().removeprefix("0x").lower()
        )
        if stored_public_key != public_key:
            raise SystemExit(f"static enode key mismatch for validator-{index}")
        address = keccak(bytes.fromhex(public_key))[-20:].hex()
        private_key = key_path.read_text(encoding="utf-8").strip()
        private_key_address = Account.from_key(private_key).address.removeprefix("0x").lower()
        if private_key_address != address:
            raise SystemExit(f"private/public key mismatch for validator-{index}")
        address_path = root / f"keys/validator-{index}/address"
        if address_path.exists():
            stored_address = (
                address_path.read_text(encoding="utf-8").strip().removeprefix("0x").lower()
            )
            if stored_address != address:
                raise SystemExit(f"key-to-address mismatch for validator-{index}")
        public_keys.add(public_key)
        endpoints.add(endpoint)
        key_addresses.add(address)
        peer_ips[f"validator-{index}"] = str(ip)

    genesis = json.loads(genesis_path.read_text(encoding="utf-8"))
    genesis_addresses = validator_addresses(genesis.get("extraData", ""))
    if key_addresses != genesis_addresses:
        raise SystemExit("validator address set does not match genesis extraData")

    compose = compose_config(root)
    services = compose.get("services", {})
    for service, expected_ip in peer_ips.items():
        networks = services.get(service, {}).get("networks", {})
        actual_ip = networks.get("besu-private", {}).get("ipv4_address")
        if actual_ip != expected_ip:
            raise SystemExit(
                f"Compose/static-nodes IP mismatch for {service}: {actual_ip} != {expected_ip}"
            )
        if services.get(service, {}).get("ports"):
            raise SystemExit(f"validator RPC/P2P port must not be exposed: {service}")

    print(f"[PASS] static peer count: {len(peers)}")
    print("[PASS] validator key/address/genesis mapping")
    print("[PASS] Compose IP/static-nodes mapping")


if __name__ == "__main__":
    main()
