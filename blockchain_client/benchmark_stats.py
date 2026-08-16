"""Statistics helpers for blockchain benchmark results."""

from statistics import fmean

from blockchain_client.benchmark_models import (
    BenchmarkRunResult,
    BenchmarkSummary,
)


def percentile(values: list[float], percentile_value: float) -> float | None:
    """Calculate a percentile using linear interpolation."""

    if not values:
        return None

    if not 0 <= percentile_value <= 100:
        raise ValueError("percentile must be between 0 and 100")

    ordered = sorted(values)

    if len(ordered) == 1:
        return ordered[0]

    position = (len(ordered) - 1) * (percentile_value / 100)
    lower_index = int(position)
    upper_index = min(lower_index + 1, len(ordered) - 1)

    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]

    fraction = position - lower_index

    return lower_value + (upper_value - lower_value) * fraction


def summarize_run(run: BenchmarkRunResult) -> BenchmarkSummary:
    """Calculate aggregate statistics for one benchmark run."""

    run.validate()

    submitted = len(run.transactions)

    successful_transactions = [
        transaction for transaction in run.transactions if transaction.success
    ]

    successful = len(successful_transactions)
    failed = submitted - successful

    duration_seconds = run.duration_seconds

    throughput_tps = (
        successful / duration_seconds
        if duration_seconds > 0
        else 0.0
    )

    success_rate = successful / submitted
    failure_rate = failed / submitted

    latencies = [
        transaction.latency_seconds
        for transaction in successful_transactions
    ]

    latency_min = min(latencies) if latencies else None
    latency_mean = fmean(latencies) if latencies else None
    latency_max = max(latencies) if latencies else None

    gas_values = [
        transaction.gas_used
        for transaction in successful_transactions
        if transaction.gas_used is not None
    ]

    gas_total = sum(gas_values)
    gas_mean = fmean(gas_values) if gas_values else None

    block_numbers = [
        transaction.block_number
        for transaction in successful_transactions
        if transaction.block_number is not None
    ]

    if block_numbers:
        first_block = min(block_numbers)
        last_block = max(block_numbers)
        unique_blocks = len(set(block_numbers))
        transactions_per_block = successful / unique_blocks
    else:
        first_block = None
        last_block = None
        unique_blocks = 0
        transactions_per_block = None

    return BenchmarkSummary(
        run_id=run.run_id,
        scenario_name=run.scenario.name,
        operation=run.scenario.operation,
        repetition=run.repetition,
        concurrency=run.scenario.concurrency,
        submitted=submitted,
        successful=successful,
        failed=failed,
        duration_seconds=duration_seconds,
        throughput_tps=throughput_tps,
        success_rate=success_rate,
        failure_rate=failure_rate,
        latency_min_seconds=latency_min,
        latency_mean_seconds=latency_mean,
        latency_p50_seconds=percentile(latencies, 50),
        latency_p95_seconds=percentile(latencies, 95),
        latency_p99_seconds=percentile(latencies, 99),
        latency_max_seconds=latency_max,
        gas_total=gas_total,
        gas_mean=gas_mean,
        first_block=first_block,
        last_block=last_block,
        blocks_used=unique_blocks,
        transactions_per_block=transactions_per_block,
    )