"""Contract artifact loading helpers."""

import json
from pathlib import Path
from typing import Any

from blockchain_client.exceptions import ConfigurationError


def load_contract_abi(artifact_path: Path) -> list[dict[str, Any]]:
    """Load an ABI from a Foundry artifact JSON file."""

    try:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigurationError(f"unable to read artifact: {artifact_path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigurationError(f"artifact is not valid JSON: {artifact_path}") from exc

    abi = artifact.get("abi")
    if not isinstance(abi, list):
        raise ConfigurationError("artifact does not contain an ABI list")
    return abi
