from concurrent.futures import ThreadPoolExecutor

import pytest

from blockchain_client.exceptions import NonceError
from blockchain_client.nonce import NonceManager


class FakeEth:
    def __init__(self, pending_nonce: int) -> None:
        self.pending_nonce = pending_nonce
        self.calls: list[tuple[str, str]] = []

    def get_transaction_count(self, address: str, block_identifier: str) -> int:
        self.calls.append((address, block_identifier))
        return self.pending_nonce


class FakeWeb3:
    def __init__(self, pending_nonce: int) -> None:
        self.eth = FakeEth(pending_nonce)


def test_nonce_manager_uses_pending_nonce() -> None:
    web3 = FakeWeb3(7)
    manager = NonceManager(web3, "0xabc")

    assert manager.next_nonce() == 7
    assert web3.eth.calls == [("0xabc", "pending")]


def test_nonce_manager_allocates_sequential_nonces() -> None:
    manager = NonceManager(FakeWeb3(7), "0xabc")

    assert [manager.next_nonce(), manager.next_nonce(), manager.next_nonce()] == [7, 8, 9]


def test_nonce_manager_is_thread_safe() -> None:
    manager = NonceManager(FakeWeb3(3), "0xabc")

    with ThreadPoolExecutor(max_workers=8) as executor:
        nonces = list(executor.map(lambda _: manager.next_nonce(), range(25)))

    assert sorted(nonces) == list(range(3, 28))
    assert len(set(nonces)) == 25


def test_nonce_manager_reset_resyncs_from_pending_state() -> None:
    web3 = FakeWeb3(1)
    manager = NonceManager(web3, "0xabc")

    assert manager.next_nonce() == 1
    web3.eth.pending_nonce = 9
    manager.reset()

    assert manager.next_nonce() == 9


def test_nonce_manager_wraps_pending_nonce_errors() -> None:
    class BrokenEth:
        def get_transaction_count(self, address: str, block_identifier: str) -> int:
            raise ValueError("provider failed")

    class BrokenWeb3:
        eth = BrokenEth()

    with pytest.raises(NonceError):
        NonceManager(BrokenWeb3(), "0xabc").next_nonce()
