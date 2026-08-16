"""Tests for concurrent benchmark execution."""

from datetime import UTC, datetime, timedelta
from threading import Lock
from time import sleep

from blockchain_client.benchmark_models import BenchmarkScenario
from blockchain_client.benchmark_runner import (
    BenchmarkRunner,
    synthetic_bytes32,
)
from blockchain_client.models import TransactionResult


class FakeEth:
    def __init__(self) -> None:
        self.receipts: dict[str, dict[str, int]] = {}

    def get_transaction_receipt(
        self,
        tx_hash: str,
    ) -> dict[str, int]:
        return self.receipts[tx_hash]


class FakeWeb3:
    def __init__(self) -> None:
        self.eth = FakeEth()


class FakeClient:
    def __init__(self) -> None:
        self.web3 = FakeWeb3()
        self.calls: list[tuple[str, str]] = []
        self.access_calls: list[tuple[str, str, str]] = []
        self.fail_sequences: set[int] = set()
        self._lock = Lock()
        self._sequence = 0

    def record_evidence(
        self,
        evidence_ref: str,
        static_hash: str,
    ) -> TransactionResult:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence

            self.calls.append(
                (
                    evidence_ref,
                    static_hash,
                )
            )

        if sequence in self.fail_sequences:
            raise RuntimeError("synthetic transaction failure")

        tx_hash = "0x" + f"{sequence:064x}"

        self.web3.eth.receipts[tx_hash] = {
            "gasUsed": 70_000 + sequence,
            "effectiveGasPrice": 10 + sequence,
            "blockNumber": 200 + sequence,
        }

        return TransactionResult(
            tx_hash=tx_hash,
            block_number=100 + sequence,
            block_timestamp=datetime(
                2026,
                8,
                12,
                8,
                0,
                tzinfo=UTC,
            ),
            contract_address="0x" + "12" * 20,
            chain_id=20260720,
            confirmations=1,
            event={},
        )

    def record_access(
        self,
        evidence_ref: str,
        officer_ref: str,
        access_session_ref: str,
    ) -> TransactionResult:
        with self._lock:
            self._sequence += 1
            sequence = self._sequence
            self.access_calls.append(
                (evidence_ref, officer_ref, access_session_ref)
            )

        tx_hash = "0x" + f"{sequence:064x}"
        self.web3.eth.receipts[tx_hash] = {
            "gasUsed": 50_000 + sequence,
            "effectiveGasPrice": 20 + sequence,
            "blockNumber": 300 + sequence,
        }
        return TransactionResult(
            tx_hash=tx_hash,
            block_number=300 + sequence,
            block_timestamp=datetime(2026, 8, 12, 8, 0, tzinfo=UTC),
            contract_address="0x" + "12" * 20,
            chain_id=20260720,
            confirmations=1,
            event={},
        )


class SequenceClock:
    def __init__(
        self,
        values: list[datetime],
    ) -> None:
        self.values = iter(values)

    def __call__(self) -> datetime:
        return next(self.values)


def make_scenario(
    *,
    transaction_count: int = 2,
    concurrency: int = 1,
    operation: str = "recordEvidence",
) -> BenchmarkScenario:
    return BenchmarkScenario(
        name="evidence-baseline",
        operation=operation,
        transaction_count=transaction_count,
        concurrency=concurrency,
        confirmations=1,
    )


def test_synthetic_bytes32_is_deterministic_and_unique() -> None:
    first = synthetic_bytes32(
        run_id="run-001",
        sequence=1,
        label="evidence",
    )

    same = synthetic_bytes32(
        run_id="run-001",
        sequence=1,
        label="evidence",
    )

    different = synthetic_bytes32(
        run_id="run-001",
        sequence=2,
        label="evidence",
    )

    assert first == same
    assert first != different

    assert first.startswith("0x")
    assert len(first) == 66


def test_sequential_runner_records_successful_transactions() -> None:
    base = datetime(
        2026,
        8,
        12,
        8,
        0,
        tzinfo=UTC,
    )

    clock = SequenceClock(
        [
            base,
            base,
            base + timedelta(seconds=2),
            base + timedelta(seconds=2),
            base + timedelta(seconds=5),
            base + timedelta(seconds=5),
        ]
    )

    client = FakeClient()

    runner = BenchmarkRunner(client, clock=clock)

    result = runner.run(
        make_scenario(),
        run_id="run-001",
    )

    assert len(result.transactions) == 2

    first = result.transactions[0]
    second = result.transactions[1]

    assert first.success is True
    assert first.latency_seconds == 2
    assert first.gas_used == 70_001
    assert first.block_number == 201
    assert first.effective_gas_price == 11

    assert second.success is True
    assert second.latency_seconds == 3
    assert second.gas_used == 70_002
    assert second.block_number == 202
    assert second.effective_gas_price == 12


def test_sequential_runner_records_failure_and_continues() -> None:
    base = datetime(
        2026,
        8,
        12,
        8,
        0,
        tzinfo=UTC,
    )

    clock = SequenceClock(
        [
            base,
            base,
            base + timedelta(seconds=1),
            base + timedelta(seconds=1),
            base + timedelta(seconds=2),
            base + timedelta(seconds=2),
        ]
    )

    client = FakeClient()
    client.fail_sequences.add(1)

    runner = BenchmarkRunner(client, clock=clock)

    result = runner.run(
        make_scenario(),
        run_id="run-failure",
    )

    assert len(result.transactions) == 2

    failed = result.transactions[0]
    successful = result.transactions[1]

    assert failed.success is False
    assert failed.error_type == "RuntimeError"
    assert failed.error_message == "synthetic transaction failure"

    assert successful.success is True

    assert len(client.calls) == 2


class ConcurrentFakeClient(FakeClient):
    def __init__(self) -> None:
        super().__init__()
        self._lock = Lock()
        self.active_calls = 0
        self.max_active_calls = 0

    def record_evidence(
        self,
        evidence_ref: str,
        static_hash: str,
    ) -> TransactionResult:
        with self._lock:
            self.active_calls += 1
            self.max_active_calls = max(
                self.max_active_calls,
                self.active_calls,
            )

        try:
            sleep(0.02)
            return super().record_evidence(
                evidence_ref,
                static_hash,
            )
        finally:
            with self._lock:
                self.active_calls -= 1

    def record_access(
        self,
        evidence_ref: str,
        officer_ref: str,
        access_session_ref: str,
    ) -> TransactionResult:
        with self._lock:
            self.active_calls += 1
            self.max_active_calls = max(
                self.max_active_calls,
                self.active_calls,
            )
        try:
            sleep(0.02)
            return super().record_access(
                evidence_ref,
                officer_ref,
                access_session_ref,
            )
        finally:
            with self._lock:
                self.active_calls -= 1


def test_runner_executes_transactions_concurrently() -> None:
    client = ConcurrentFakeClient()
    runner = BenchmarkRunner(client)
    scenario = make_scenario(transaction_count=8, concurrency=4)

    result = runner.run(scenario, run_id="run-concurrent")

    assert len(result.transactions) == 8
    assert all(transaction.success for transaction in result.transactions)
    assert client.max_active_calls > 1
    assert client.max_active_calls <= 4


def test_runner_returns_transactions_sorted_by_sequence() -> None:
    client = ConcurrentFakeClient()
    runner = BenchmarkRunner(client)
    scenario = make_scenario(transaction_count=6, concurrency=3)

    result = runner.run(scenario, run_id="run-order")

    assert [transaction.sequence for transaction in result.transactions] == [
        1,
        2,
        3,
        4,
        5,
        6,
    ]


def test_access_workload_prepares_evidence_and_records_access() -> None:
    client = FakeClient()
    runner = BenchmarkRunner(client)

    result = runner.run(
        make_scenario(transaction_count=3, operation="recordAccess"),
        run_id="run-access",
    )

    assert len(client.calls) == 3
    assert len(client.access_calls) == 3
    assert len({call[0] for call in client.calls}) == 3
    assert [call[0] for call in client.access_calls] == [
        call[0] for call in client.calls
    ]
    assert len(result.transactions) == 3
    assert all(transaction.success for transaction in result.transactions)
    assert all(
        transaction.operation == "recordAccess"
        for transaction in result.transactions
    )


def test_access_workload_supports_concurrency() -> None:
    client = ConcurrentFakeClient()
    runner = BenchmarkRunner(client)

    result = runner.run(
        make_scenario(
            transaction_count=8,
            concurrency=4,
            operation="recordAccess",
        ),
        run_id="run-access-concurrent",
    )

    assert len(client.calls) == 8
    assert len(client.access_calls) == 8
    assert all(transaction.success for transaction in result.transactions)
    assert client.max_active_calls > 1
    assert client.max_active_calls <= 4
