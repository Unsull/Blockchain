# Blockchain Benchmark

This directory contains the reproducible benchmark configuration and methodology for Phase 2.5C performance evaluation of the local Hyperledger Besu QBFT network.

The benchmark measures application-level transaction performance together with network and resource observations collected from Prometheus.

## Goals

The benchmark is designed to answer the following questions:

* How long does an EvidenceRegistry write transaction take to complete?
* How does transaction latency change as concurrency increases?
* How many successful transactions per second can the local network process?
* Does the transaction failure rate increase under higher concurrency?
* How much gas is consumed by each EvidenceRegistry operation?
* How are successful transactions distributed across blocks?
* Does transaction-pool pressure increase during benchmark execution?
* Do validator or RPC nodes become unavailable during the test?
* How do CPU and memory observations change during benchmark execution?

The results describe this specific local benchmark environment. They must not be interpreted as universal Hyperledger Besu or production-network capacity.

## Network Under Test

The benchmark targets the local Hyperledger Besu QBFT environment used by this project.

The current environment consists of:

* 4 QBFT validator nodes
* 1 RPC node
* Prometheus monitoring
* Grafana visualization
* EvidenceRegistry smart contract
* a single-host Docker-based execution environment

All benchmark transactions are submitted through the configured RPC endpoint.

Because all nodes currently run on one host, host CPU, memory, Docker scheduling, disk I/O, and other local workloads may influence benchmark results.

## Workloads

Two EvidenceRegistry write operations are measured.

### `recordEvidence`

Records a new evidence reference and static evidence hash.

Each measured transaction uses unique synthetic `bytes32` values generated specifically for the benchmark.

No real case identifiers, evidence identifiers, officer identifiers, or personal data are required.

### `recordAccess`

Records an access event for an existing evidence reference.

The smart contract requires the referenced evidence to exist before `recordAccess` can succeed.

For this reason, the benchmark runner prepares one unique evidence record for each access transaction before measured execution begins.

Evidence preparation is excluded from:

* access latency
* access throughput
* measured access transaction count

This prevents setup work from inflating the measured performance cost of `recordAccess`.

## Scenario Matrix

Each operation is tested at four concurrency levels:

* 1
* 2
* 5
* 10

Each scenario uses:

* 20 measured transactions
* 1 required confirmation
* 3 repetitions

The complete matrix is:

| Scenario       | Operation        | Transactions | Concurrency | Confirmations | Repetitions |
| -------------- | ---------------- | -----------: | ----------: | ------------: | ----------: |
| `evidence-c1`  | `recordEvidence` |           20 |           1 |             1 |           3 |
| `evidence-c2`  | `recordEvidence` |           20 |           2 |             1 |           3 |
| `evidence-c5`  | `recordEvidence` |           20 |           5 |             1 |           3 |
| `evidence-c10` | `recordEvidence` |           20 |          10 |             1 |           3 |
| `access-c1`    | `recordAccess`   |           20 |           1 |             1 |           3 |
| `access-c2`    | `recordAccess`   |           20 |           2 |             1 |           3 |
| `access-c5`    | `recordAccess`   |           20 |           5 |             1 |           3 |
| `access-c10`   | `recordAccess`   |           20 |          10 |             1 |           3 |

This produces:

```text
2 operations
× 4 concurrency levels
× 3 repetitions
= 24 measured benchmark runs
```

The canonical scenario configuration is stored in:

```text
network/besu/benchmarks/scenarios.json
```

## Primary Application Metrics

The benchmark runner records one result for every measured transaction.

### Successful throughput

Successful throughput is calculated as:

```text
successful transactions
-----------------------
benchmark duration
```

and is reported as transactions per second (`tx/s`).

Failed transactions are not counted as successful throughput.

### Success and failure rate

Each measured transaction is classified as either:

* successful
* failed

Failures remain part of the benchmark dataset and are not silently discarded.

Failure records include an error type and sanitized error message where available.

### Transaction latency

Latency represents end-to-end execution time for a measured operation.

The benchmark reports:

* minimum latency
* mean latency
* P50 latency
* P95 latency
* P99 latency
* maximum latency

Latency statistics are calculated from successful measured transactions.

### Gas usage

For successful transactions, the benchmark records receipt-derived gas usage.

Summary statistics include:

* total gas used
* mean gas used

Gas measurements are useful for comparing EvidenceRegistry operations.

They must not automatically be interpreted as real monetary cost because this benchmark runs on a private network.

### Block distribution

Successful transactions also record their block number.

The benchmark derives:

* first block used
* last block used
* number of unique blocks used
* average successful transactions per used block

## Concurrency

`transaction_count` and `concurrency` represent different concepts.

For example:

```text
transaction_count = 20
concurrency = 5
```

means that 20 measured transactions are submitted using a worker pool with up to 5 concurrently executing tasks.

The final output remains ordered by transaction sequence even when transactions finish in a different order.

## Transaction Failure Handling

A single failed transaction does not terminate the complete benchmark run.

The runner records the failure and continues processing the remaining workload.

A failed transaction result may include:

* sequence number
* operation
* start time
* finish time
* latency
* error type
* sanitized error message

This allows the benchmark to report both throughput and reliability under increasing load.

## Network Observation

Each measured benchmark repetition captures Prometheus snapshots immediately before and immediately after measured transaction execution.

Prometheus observation is separate from client-side transaction measurement.

Observed categories include:

* Besu target availability
* blockchain height
* peer count
* transaction-pool size
* chain-head transaction count
* JVM memory
* process resident memory
* process CPU rate
* active RPC connections
* synchronization status

The default Prometheus endpoint is:

```text
http://127.0.0.1:9090
```

It may be overridden using:

```text
PROMETHEUS_URL
```

or:

```text
--prometheus-url
```

### Prometheus interpretation

Prometheus is used for network and resource observation only.

The benchmark client remains the source of truth for:

* transaction throughput
* latency
* success/failure
* transaction hash
* block number
* gas usage
* confirmations

The Besu chain-head transaction-count metric describes the current chain-head block. It must not be interpreted as the cumulative number of EvidenceRegistry application transactions.

Prometheus currently scrapes the Besu nodes at fixed intervals. Short benchmark runs may therefore have limited temporal resolution and may not contain a scrape for every transaction-bearing block.

## Network Health Requirement

Before measured execution begins, the benchmark expects Prometheus to report all five Besu targets as available.

The expected targets are:

* validator 1
* validator 2
* validator 3
* validator 4
* RPC node

If the expected target count is incorrect or any target reports `up != 1`, the benchmark observation validation fails.

The network is checked again after measured transaction execution.

This prevents benchmark results from being accepted without recording obvious node-availability failures.

## Runtime Configuration

The benchmark CLI requires the following runtime configuration:

* `RPC_URL`
* `CHAIN_ID`
* `CONTRACT_ADDRESS`
* `WRITER_PRIVATE_KEY`

Optional configuration includes:

* `ARTIFACT_PATH`
* `PROMETHEUS_URL`

Secrets must be supplied through the ignored local runtime environment.

Private keys must never be placed in:

* `scenarios.json`
* benchmark source code
* committed documentation
* benchmark result files
* Git history

## CLI

The benchmark command is:

```bash
python network/besu/scripts/benchmark-transactions.py
```

By default, the CLI loads:

```text
network/besu/benchmarks/scenarios.json
```

and writes runtime output under:

```text
network/besu/benchmarks/results/
```

### Run one scenario

For initial validation, run only one scenario:

```bash
python network/besu/scripts/benchmark-transactions.py \
  --scenario evidence-c1
```

### Run selected scenarios

Multiple scenario arguments may be supplied:

```bash
python network/besu/scripts/benchmark-transactions.py \
  --scenario evidence-c1 \
  --scenario evidence-c5
```

### Override the scenario file

```bash
python network/besu/scripts/benchmark-transactions.py \
  --scenario-file network/besu/benchmarks/scenarios.json
```

### Override the output directory

```bash
python network/besu/scripts/benchmark-transactions.py \
  --output-directory network/besu/benchmarks/results
```

### Override Prometheus

```bash
python network/besu/scripts/benchmark-transactions.py \
  --prometheus-url http://127.0.0.1:9090
```

## Output Files

Each measured repetition produces four runtime files.

### Raw run JSON

```text
run-<run_id>.json
```

Contains:

* scenario configuration
* repetition number
* benchmark start and finish timestamps
* run duration
* individual transaction results

### Per-transaction CSV

```text
transactions-<run_id>.csv
```

Contains one row for each measured transaction.

This format is intended for:

* spreadsheet analysis
* pandas
* chart generation
* statistical analysis

### Summary JSON

```text
summary-<run_id>.json
```

Contains aggregated statistics including:

* submitted transactions
* successful transactions
* failed transactions
* successful throughput
* success rate
* failure rate
* latency statistics
* gas statistics
* block distribution

### Network observation JSON

```text
network-<run_id>.json
```

Contains Prometheus snapshots captured before and after measured execution.

The observation includes the benchmark `run_id`, Prometheus endpoint, capture timestamps, metric names, instances, and values.

## Example Runtime Output Directory

A benchmark session may produce files such as:

```text
network/besu/benchmarks/results/
├── run-abc123.json
├── transactions-abc123.csv
├── summary-abc123.json
├── network-abc123.json
├── run-def456.json
├── transactions-def456.csv
├── summary-def456.json
└── network-def456.json
```

Runtime output is intentionally excluded from Git.

The directory is ignored through:

```text
network/besu/benchmarks/results/
```

## Recommended Execution Procedure

Do not begin by running the complete 24-run matrix.

Use the following validation sequence.

### 1. Validate code offline

Run unit tests, Ruff, Mypy, and Python compilation first.

### 2. Start the Besu environment

Confirm:

* RPC node is reachable
* all validators are running
* Prometheus is reachable
* all five Besu targets are UP
* contract bytecode exists at the configured address
* the configured writer has the required role

### 3. Run a small baseline scenario

Start with:

```text
evidence-c1
```

Do not immediately run the complete matrix.

Validate that:

* all measured transactions succeed
* result JSON is valid
* transaction CSV is valid
* summary JSON is valid
* network observation JSON is valid
* no secret is present in output
* Prometheus reports five UP targets

### 4. Validate higher concurrency

After the baseline succeeds, test progressively:

```text
1 → 2 → 5 → 10
```

This makes nonce, transaction-pool, timeout, or resource-pressure problems easier to identify.

### 5. Run the complete matrix

Only after the runtime pipeline is validated should all configured scenarios and repetitions be executed.

## Repetition Policy

Each scenario is repeated three times to reduce reliance on a single measurement.

Results should be analyzed across repetitions rather than selecting only the fastest run.

When reporting final performance, retain all valid repetitions and document any invalidated run and the reason for invalidation.

## Result Interpretation

Benchmark results must be interpreted within the measured environment.

A result such as:

```text
throughput = X tx/s
```

means:

> The tested local single-host Besu QBFT configuration achieved the measured successful throughput under the specified benchmark workload and concurrency.

It does not mean:

> Hyperledger Besu universally supports exactly X tx/s.

Performance depends on factors including:

* CPU
* memory
* disk
* Docker scheduling
* operating system
* Besu configuration
* block timing
* smart-contract workload
* RPC behavior
* confirmation requirement
* transaction concurrency

## Research Reporting

For the final Phase 2.5C report, recommended comparisons include:

* concurrency vs successful throughput
* concurrency vs P50 latency
* concurrency vs P95 latency
* concurrency vs P99 latency
* concurrency vs failure rate
* `recordEvidence` vs `recordAccess` gas usage
* transactions per block
* transaction-pool observations
* CPU observations
* memory observations
* node availability throughout benchmark execution

The report should explicitly state that the benchmark was performed in a local single-host Docker-based private QBFT environment.

## Security and Data Handling

Benchmark references are synthetic.

The benchmark must not use:

* real evidence identifiers
* real case numbers
* real officer identities
* personal information

Runtime result files must not contain:

* writer private keys
* deployer private keys
* administrator private keys
* passwords
* `.env` contents

Before committing Phase 2.5C implementation, perform a final secret scan and confirm that the ignored runtime result directory has not been staged.

## Reproducibility

### Final Analysis

Generate the final aggregate analysis from a completed matrix directory:

```text
python network/besu/scripts/analyze-benchmark-results.py \
  network/besu/benchmarks/results/<matrix-directory>
```

The command writes `analysis/aggregate.csv`, `analysis/aggregate.json`, and
`analysis/benchmark-report.md`. Application throughput, latency, gas, and
transaction outcomes remain measured benchmark results; Prometheus network
observations provide availability, synchronization, peer-connectivity,
block-height divergence, and chain-progress context. The highest observed TPS
within the tested matrix is not a maximum-capacity measurement.

Runtime result directories remain ignored by Git and should not be committed.

The benchmark configuration is version-controlled through:

```text
network/besu/benchmarks/scenarios.json
```

The benchmark implementation, scenario matrix, methodology, and analysis logic should be committed.

Generated runtime measurements should remain excluded from Git unless a deliberately sanitized research artifact is later selected for publication.

## Scope Limitation

This benchmark evaluates application transactions and network behavior in the current project environment.

It is not:

* production capacity planning
* a distributed multi-host benchmark
* an internet-scale load test
* a long-duration soak test
* a chaos test
* a universal Besu performance claim

These limitations should remain explicit when benchmark results are presented in the final project report.
