from dataclasses import dataclass
from typing import Any

import pytest

from blockchain_client.exceptions import TransactionSigningError
from blockchain_client.signer import LocalPrivateKeySigner


@dataclass(frozen=True)
class SignedWithSnakeCase:
    raw_transaction: bytes


@dataclass(frozen=True)
class SignedWithCamelCase:
    rawTransaction: bytes


def test_local_signer_supports_raw_transaction_attribute(monkeypatch: pytest.MonkeyPatch) -> None:
    signer = LocalPrivateKeySigner("0x" + "1" * 64)

    monkeypatch.setattr(signer._account, "sign_transaction", lambda tx: SignedWithSnakeCase(b"raw"))

    assert signer.sign_transaction({"nonce": 1}) == b"raw"


def test_local_signer_supports_legacy_raw_transaction_attribute(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    signer = LocalPrivateKeySigner("0x" + "1" * 64)

    monkeypatch.setattr(signer._account, "sign_transaction", lambda tx: SignedWithCamelCase(b"raw"))

    assert signer.sign_transaction({"nonce": 1}) == b"raw"


def test_local_signer_wraps_signing_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    signer = LocalPrivateKeySigner("0x" + "1" * 64)

    def fail(transaction: dict[str, Any]) -> object:
        raise ValueError("bad transaction")

    monkeypatch.setattr(signer._account, "sign_transaction", fail)

    with pytest.raises(TransactionSigningError):
        signer.sign_transaction({"nonce": 1})
