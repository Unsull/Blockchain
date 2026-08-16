"""Typed data models for blockchain benchmark execution."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

BenchmarkOperation = Literal["recordEvidence", "recordAccess"]


@dataclass(frozen=True)
class BenchmarkScenario:
    """Configuration for one benchmark scenario."""

    name: str
    operation: BenchmarkOperation
    transaction_count: int
    concurrency: int
    confirmations: int

    def validate(self) -> None:
        """Validate benchmark scenario configuration."""

        if not self.name.strip():
            raise ValueError("benchmark scenario name is required")
        if self.transaction_count <= 0:
            raise ValueError("transaction_count must be positive")
        if self.concurrency <= 0:
            raise ValueError("concurrency must be positive")
        if self.concurrency > self.transaction_count:
            raise ValueError("concurrency cannot exceed transaction_count")
        if self.confirmations < 0:
            raise ValueError("confirmations cannot be negative")


@dataclass(frozen=True)
class BenchmarkTransactionResult:
    """Result of one benchmark transaction."""

    sequence: int
    operation: BenchmarkOperation
    started_at: datetime
    finished_at: datetime
    success: bool

    tx_hash: str | None = None
    block_number: int | None = None
    gas_used: int | None = None
    effective_gas_price: int | None = None
    confirmations: int | None = None

    error_type: str | None = None
    error_message: str | None = None

    @property
    def latency_seconds(self) -> float:
        """Return end-to-end transaction latency in seconds."""

        return (self.finished_at - self.started_at).total_seconds()

    def validate(self) -> None:
        """Validate one transaction benchmark result."""

        if self.sequence <= 0:
            raise ValueError("sequence must be positive")

        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")

        if self.finished_at.tzinfo is None:
            raise ValueError("finished_at must be timezone-aware")

        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot be before started_at")

        if self.success:
            if not self.tx_hash:
                raise ValueError("successful transaction requires tx_hash")
            if self.block_number is None:
                raise ValueError("successful transaction requires block_number")
            if self.gas_used is None:
                raise ValueError("successful transaction requires gas_used")
            if self.confirmations is None:
                raise ValueError("successful transaction requires confirmations")
        elif not self.error_type:
            raise ValueError("failed transaction requires error_type")


@dataclass(frozen=True)
class BenchmarkRunResult:
    """Complete result of one benchmark scenario execution."""

    run_id: str
    scenario: BenchmarkScenario
    repetition: int
    started_at: datetime
    finished_at: datetime
    transactions: tuple[BenchmarkTransactionResult, ...]

    @property
    def duration_seconds(self) -> float:
        """Return total benchmark run duration in seconds."""

        return (self.finished_at - self.started_at).total_seconds()

    def validate(self) -> None:
        """Validate consistency of a complete benchmark run."""

        if not self.run_id.strip():
            raise ValueError("run_id is required")

        if self.repetition <= 0:
            raise ValueError("repetition must be positive")

        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware")

        if self.finished_at.tzinfo is None:
            raise ValueError("finished_at must be timezone-aware")

        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot be before started_at")

        self.scenario.validate()

        if len(self.transactions) != self.scenario.transaction_count:
            raise ValueError(
                "transaction result count does not match scenario transaction_count"
            )

        for transaction in self.transactions:
            transaction.validate()

            if transaction.operation != self.scenario.operation:
                raise ValueError(
                    "transaction operation does not match benchmark scenario"
                )

@dataclass(frozen=True)
class BenchmarkSummary:
    """Aggregated statistics for one benchmark run."""

    run_id: str
    scenario_name: str
    operation: BenchmarkOperation
    repetition: int
    concurrency: int

    submitted: int
    successful: int
    failed: int

    duration_seconds: float
    throughput_tps: float
    success_rate: float
    failure_rate: float

    latency_min_seconds: float | None
    latency_mean_seconds: float | None
    latency_p50_seconds: float | None
    latency_p95_seconds: float | None
    latency_p99_seconds: float | None
    latency_max_seconds: float | None

    gas_total: int
    gas_mean: float | None

    first_block: int | None
    last_block: int | None
    blocks_used: int
    transactions_per_block: float | None