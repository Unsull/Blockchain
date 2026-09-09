from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from time import sleep

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


def test_nonce_manager_reconciles_when_pending_nonce_moves_back_after_restart() -> None:
    web3 = FakeWeb3(7)
    manager = NonceManager(web3, "0xabc")

    with manager.reserve_nonce() as nonce:
        assert nonce == 7
    web3.eth.pending_nonce = 6

    with manager.reserve_nonce() as nonce:
        assert nonce == 6


def test_nonce_manager_is_thread_safe() -> None:
    web3 = FakeWeb3(3)
    manager = NonceManager(web3, "0xabc")
    state_lock = Lock()
    active_reservations = 0
    maximum_active = 0

    def reserve_and_broadcast(_: int) -> int:
        nonlocal active_reservations, maximum_active
        with manager.reserve_nonce() as nonce:
            with state_lock:
                active_reservations += 1
                maximum_active = max(maximum_active, active_reservations)
            sleep(0.001)
            web3.eth.pending_nonce += 1
            with state_lock:
                active_reservations -= 1
            return nonce

    with ThreadPoolExecutor(max_workers=8) as executor:
        nonces = list(executor.map(reserve_and_broadcast, range(25)))

    assert sorted(nonces) == list(range(3, 28))
    assert len(set(nonces)) == 25
    assert maximum_active == 1


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
