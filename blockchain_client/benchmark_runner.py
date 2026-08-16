"""Concurrent benchmark execution for EvidenceRegistry transactions."""

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any, Protocol
from uuid import uuid4

from blockchain_client.benchmark_models import (
    BenchmarkRunResult,
    BenchmarkScenario,
    BenchmarkTransactionResult,
)
from blockchain_client.models import TransactionResult


class BenchmarkClient(Protocol):
    """Client behavior required by the benchmark runner."""

    web3: Any

    def record_evidence(
        self,
        evidence_ref: str,
        static_hash: str,
    ) -> TransactionResult:
        """Record one synthetic evidence transaction."""

    def record_access(
        self,
        evidence_ref: str,
        officer_ref: str,
        access_session_ref: str,
    ) -> TransactionResult:
        """Record one synthetic access transaction."""

def utc_now() -> datetime:
    """Return the current timezone-aware UTC timestamp."""

    return datetime.now(UTC)


def synthetic_bytes32(
    *,
    run_id: str,
    sequence: int,
    label: str,
) -> str:
    """Create a deterministic synthetic bytes32 value for benchmark data."""

    payload = f"phase-2.5c:{run_id}:{sequence}:{label}"
    return "0x" + sha256(payload.encode()).hexdigest()


class BenchmarkRunner:
    """Execute benchmark scenarios against an EvidenceRegistry client."""

    def __init__(
        self,
        client: BenchmarkClient,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self.client = client
        self.clock = clock

    def run(
        self,
        scenario: BenchmarkScenario,
        *,
        repetition: int = 1,
        run_id: str | None = None,
    ) -> BenchmarkRunResult:
        """Execute one benchmark scenario."""

        scenario.validate()

        if repetition <= 0:
            raise ValueError("repetition must be positive")

        actual_run_id = run_id or uuid4().hex
        access_evidence = (
            self._prepare_access_evidence(
                run_id=actual_run_id,
                transaction_count=scenario.transaction_count,
            )
            if scenario.operation == "recordAccess"
            else {}
        )

        started_at = self.clock()

        with ThreadPoolExecutor(
            max_workers=scenario.concurrency,
        ) as executor:
            futures = {
                executor.submit(
                    self._execute_transaction,
                    scenario=scenario,
                    run_id=actual_run_id,
                    sequence=sequence,
                    prepared_evidence_ref=access_evidence.get(sequence),
                ): sequence
                for sequence in range(
                    1,
                    scenario.transaction_count + 1,
                )
            }

            transactions = [
                future.result()
                for future in as_completed(futures)
            ]

        transactions.sort(
            key=lambda transaction: transaction.sequence
        )

        finished_at = self.clock()

        result = BenchmarkRunResult(
            run_id=actual_run_id,
            scenario=scenario,
            repetition=repetition,
            started_at=started_at,
            finished_at=finished_at,
            transactions=tuple(transactions),
        )

        result.validate()

        return result

    def _execute_transaction(
        self,
        *,
        scenario: BenchmarkScenario,
        run_id: str,
        sequence: int,
        prepared_evidence_ref: str | None,
    ) -> BenchmarkTransactionResult:
        started_at = self.clock()

        try:
            if scenario.operation == "recordEvidence":
                result = self._record_evidence(
                    run_id=run_id,
                    sequence=sequence,
                )
            elif scenario.operation == "recordAccess":
                if prepared_evidence_ref is None:
                    raise ValueError("prepared access evidence is required")
                result = self._record_access(
                    run_id=run_id,
                    sequence=sequence,
                    evidence_ref=prepared_evidence_ref,
                )
            else:
                raise ValueError(
                    f"unsupported benchmark operation: {scenario.operation}"
                )

            receipt = self.client.web3.eth.get_transaction_receipt(
                result.tx_hash
            )

            gas_used = int(receipt["gasUsed"])
            block_number = int(receipt["blockNumber"])

            effective_gas_price_raw = receipt.get(
                "effectiveGasPrice"
            )

            effective_gas_price = (
                int(effective_gas_price_raw)
                if effective_gas_price_raw is not None
                else None
            )

            finished_at = self.clock()

            return BenchmarkTransactionResult(
                sequence=sequence,
                operation=scenario.operation,
                started_at=started_at,
                finished_at=finished_at,
                success=True,
                tx_hash=result.tx_hash,
                block_number=block_number,
                gas_used=gas_used,
                effective_gas_price=effective_gas_price,
                confirmations=result.confirmations,
            )

        except Exception as exc:
            finished_at = self.clock()

            return BenchmarkTransactionResult(
                sequence=sequence,
                operation=scenario.operation,
                started_at=started_at,
                finished_at=finished_at,
                success=False,
                error_type=type(exc).__name__,
                error_message=str(exc),
            )

    def _prepare_access_evidence(
        self,
        *,
        run_id: str,
        transaction_count: int,
    ) -> dict[int, str]:
        prepared: dict[int, str] = {}
        for sequence in range(1, transaction_count + 1):
            evidence_ref = synthetic_bytes32(
                run_id=run_id,
                sequence=sequence,
                label="access-evidence",
            )
            static_hash = synthetic_bytes32(
                run_id=run_id,
                sequence=sequence,
                label="access-static-hash",
            )
            self.client.record_evidence(evidence_ref, static_hash)
            prepared[sequence] = evidence_ref
        return prepared

    def _record_evidence(
        self,
        *,
        run_id: str,
        sequence: int,
    ) -> TransactionResult:
        evidence_ref = synthetic_bytes32(
            run_id=run_id,
            sequence=sequence,
            label="evidence",
        )
        static_hash = synthetic_bytes32(
            run_id=run_id,
            sequence=sequence,
            label="static-hash",
        )
        return self.client.record_evidence(evidence_ref, static_hash)

    def _record_access(
        self,
        *,
        run_id: str,
        sequence: int,
        evidence_ref: str,
    ) -> TransactionResult:
        officer_ref = synthetic_bytes32(
            run_id=run_id,
            sequence=sequence,
            label="officer",
        )
        access_session_ref = synthetic_bytes32(
            run_id=run_id,
            sequence=sequence,
            label="access-session",
        )
        return self.client.record_access(
            evidence_ref,
            officer_ref,
            access_session_ref,
        )
