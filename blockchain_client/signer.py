"""Transaction signer abstractions."""

from typing import Any, Protocol, cast

from eth_account import Account

from blockchain_client.exceptions import TransactionSigningError


class TransactionSigner(Protocol):
    """Protocol for pluggable transaction signers."""

    @property
    def address(self) -> str:
        """Return the signer address."""

    def sign_transaction(self, transaction: dict[str, Any]) -> bytes:
        """Sign a transaction and return raw signed transaction bytes."""


class LocalPrivateKeySigner:
    """Local private-key signer for controlled backend environments."""

    def __init__(self, private_key: str) -> None:
        self._account = Account.from_key(private_key)

    @property
    def address(self) -> str:
        """Return the derived account address."""

        return cast(str, self._account.address)

    def sign_transaction(self, transaction: dict[str, Any]) -> bytes:
        """Sign a transaction with eth-account compatibility handling."""

        try:
            signed = self._account.sign_transaction(transaction)
            raw_transaction = getattr(signed, "raw_transaction", None)
            if raw_transaction is None:
                raw_transaction = signed.rawTransaction
            return bytes(raw_transaction)
        except Exception as exc:
            raise TransactionSigningError("failed to sign transaction") from exc
