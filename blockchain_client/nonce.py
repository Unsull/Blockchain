"""Thread-safe nonce allocation."""

from threading import Lock
from typing import Any

from blockchain_client.exceptions import NonceError


class NonceManager:
    """Allocate nonces from pending chain state without reuse per client instance."""

    def __init__(self, web3: Any, address: str) -> None:
        self._web3 = web3
        self._address = address
        self._lock = Lock()
        self._next_nonce: int | None = None

    def next_nonce(self) -> int:
        """Return the next nonce, syncing from pending state when needed."""

        with self._lock:
            try:
                pending_nonce = self._web3.eth.get_transaction_count(self._address, "pending")
            except Exception as exc:
                raise NonceError("failed to fetch pending nonce") from exc
            if self._next_nonce is None or self._next_nonce < pending_nonce:
                self._next_nonce = pending_nonce
            nonce = self._next_nonce
            self._next_nonce += 1
            return nonce

    def reset(self) -> None:
        """Clear local nonce cache so the next call resyncs from pending state."""

        with self._lock:
            self._next_nonce = None
