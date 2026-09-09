"""Thread-safe nonce reservation."""

from collections.abc import Iterator
from contextlib import contextmanager
from threading import Lock
from typing import Any

from blockchain_client.exceptions import NonceError


class NonceManager:
    """Serialize nonce selection against the RPC pending state."""

    def __init__(self, web3: Any, address: str) -> None:
        self._web3 = web3
        self._address = address
        self._lock = Lock()

    @contextmanager
    def reserve_nonce(self) -> Iterator[int]:
        """Hold the writer lock while one caller builds and broadcasts a transaction."""

        with self._lock:
            # การเชื่อมต่อ Blockchain: อ่าน pending nonce ใหม่ทุกครั้งเพื่อให้ RPC restart
            # ที่ล้าง txpool สามารถทำให้ nonce ถอยกลับไปเติมช่องว่างเดิมได้อย่างปลอดภัย
            yield self._pending_nonce()

    def next_nonce(self) -> int:
        """Return the current RPC pending nonce for read-only diagnostics."""

        with self._lock:
            return self._pending_nonce()

    def reset(self) -> None:
        """Retain the compatibility hook; nonce state is no longer cached locally."""

    def _pending_nonce(self) -> int:
        try:
            return int(
                self._web3.eth.get_transaction_count(self._address, "pending")
            )
        except Exception as exc:
            raise NonceError("failed to fetch pending nonce") from exc
