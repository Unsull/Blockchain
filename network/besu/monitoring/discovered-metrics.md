# Besu 26.7.0 Discovered Prometheus Metrics

## Environment

- Besu version: 26.7.0
- Node count: 5
- Validator count: 4
- RPC node count: 1
- Prometheus scrape interval: 15s
- Discovery timestamp (UTC): 2026-08-04T03:25:20.459293+00:00

## Target Status

| Instance | Health | Last scrape | Scrape duration (s) | Last error |
| --- | --- | --- | ---: | --- |
| rpc-node:9545 | up | 2026-08-04T03:25:07.691307881Z | 0.042897341 | - |
| validator-1:9545 | up | 2026-08-04T03:25:10.514261779Z | 0.034348074 | - |
| validator-2:9545 | up | 2026-08-04T03:25:10.016033724Z | 0.039937967 | - |
| validator-3:9545 | up | 2026-08-04T03:25:13.201035221Z | 0.025018897 | - |
| validator-4:9545 | up | 2026-08-04T03:25:07.991251577Z | 0.029311279 | - |

## Discovered Metrics

### `besu_bal_blocks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_block_processing_conflicted_transactions_counter_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_block_processing_parallelized_transactions_counter_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_block_processing_state_root_calculation_duration_seconds`

- Result type: vector
- Labels: __name__, instance, job, quantile
- Sample value: `0.000111541`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_block_processing_state_root_calculation_duration_seconds_count`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `52`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_block_processing_state_root_calculation_duration_seconds_sum`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0.010140167000000002`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_chain_head_gas_limit`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `9007199254740991`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_chain_head_gas_used`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_chain_head_gas_used_counter_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_chain_head_timestamp`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1785813907`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_chain_head_transaction_count`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: transaction count
- Limitations: Describes chain-head transactions, not application evidence records.

### `besu_blockchain_chain_head_transaction_count_counter_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Describes chain-head transactions, not application evidence records.

### `besu_blockchain_difficulty`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1647`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_account_flat_database_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_account_missing_flat_database_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_account_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_storagevalue_flat_database_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_storagevalue_missing_flat_database_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_blockchain_get_storagevalue_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_bfttimerexecutor_qbft_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: QBFT or consensus metrics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_bfttimerexecutor_qbft_completed_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `49`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_bfttimerexecutor_qbft_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_bfttimerexecutor_qbft_queue_length_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `3`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_bfttimerexecutor_qbft_rejected_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_bfttimerexecutor_qbft_submitted_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `52`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Executor activity only; it does not expose validator votes or quorum.

### `besu_executors_ethscheduler_blockcreation_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_blockcreation_completed_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `14`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_blockcreation_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `2`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_blockcreation_queue_length_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_blockcreation_rejected_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_blockcreation_submitted_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `14`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_chaindatapruner_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_chaindatapruner_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_computation_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_computation_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_services_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_services_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `3`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_timer_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_timer_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_completed_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_dropped_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_queue_length_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_rejected_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_transactions_submitted_tasks_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_workers_active_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_executors_ethscheduler_workers_pool_size_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `8`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_network_vertx_eventloop_pending_tasks`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_network_vertx_worker_pool_completed_total`

- Result type: vector
- Labels: __name__, instance, job, poolName, poolType
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_network_vertx_worker_pool_rejected_total`

- Result type: vector
- Labels: __name__, instance, job, poolName, poolType
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_network_vertx_worker_pool_submitted_total`

- Result type: vector
- Labels: __name__, instance, job, poolName, poolType
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_peers_connected_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `4`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_disconnected_total`

- Result type: vector
- Labels: __name__, disconnectReason, initiator, instance, job
- Sample value: `1`
- Instances (up to 5 sampled series): validator-2:9545, validator-3:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_inflight_request_gauge`

- Result type: vector
- Labels: __name__, instance, job, taskName
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_peer_count_by_client`

- Result type: vector
- Labels: __name__, client, instance, job
- Sample value: `4`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_pending_peer_requests_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_request_time`

- Result type: vector
- Labels: __name__, instance, job, quantile, taskName
- Sample value: `0.004526458`
- Instances (up to 5 sampled series): validator-2:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_request_time_count`

- Result type: vector
- Labels: __name__, instance, job, taskName
- Sample value: `5`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_peers_request_time_sum`

- Result type: vector
- Labels: __name__, instance, job, taskName
- Sample value: `0.45808915600000005`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `besu_rpc_active_http_connection_count`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545
- Likely dashboard use: RPC metrics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_rpc_request_time`

- Result type: vector
- Labels: none
- Sample value: `no sample`
- Instances (up to 5 sampled series): none in bounded sample
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_rpc_request_time_count`

- Result type: vector
- Labels: none
- Sample value: `no sample`
- Instances (up to 5 sampled series): none in bounded sample
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_rpc_request_time_sum`

- Result type: vector
- Labels: none
- Sample value: `no sample`
- Instances (up to 5 sampled series): none in bounded sample
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_chain_download_pipeline_processed_total`

- Result type: vector
- Labels: none
- Sample value: `no sample`
- Instances (up to 5 sampled series): none in bounded sample
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_chain_download_pipeline_restarts_total`

- Result type: vector
- Labels: __name__, instance, job, reason
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_in_sync`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: sync status
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_sync_duration_bucket`

- Result type: vector
- Labels: __name__, instance, job, le, name
- Sample value: `0`
- Instances (up to 5 sampled series): validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_sync_duration_count`

- Result type: vector
- Labels: __name__, instance, job, name
- Sample value: `0`
- Instances (up to 5 sampled series): validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_sync_duration_sum`

- Result type: vector
- Labels: __name__, instance, job, name
- Sample value: `0`
- Instances (up to 5 sampled series): validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_task`

- Result type: vector
- Labels: __name__, instance, job, quantile, taskName
- Sample value: `0.000451426`
- Instances (up to 5 sampled series): validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_task_count`

- Result type: vector
- Labels: __name__, instance, job, taskName
- Sample value: `9`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_synchronizer_task_sum`

- Result type: vector
- Labels: __name__, instance, job, taskName
- Sample value: `0.093371647`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_blob_cache_size`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_blob_map_size`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_messages_expired_total`

- Result type: vector
- Labels: __name__, instance, job, message
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_number_of_transactions`

- Result type: vector
- Labels: __name__, instance, job, layer
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: transaction pool
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_number_of_transactions_by_type`

- Result type: vector
- Labels: __name__, instance, job, layer, type
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_space_used`

- Result type: vector
- Labels: __name__, instance, job, layer
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `besu_transaction_pool_unique_senders`

- Result type: vector
- Labels: __name__, instance, job, layer
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `ethereum_best_known_block_number`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1646`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `ethereum_blockchain_finalized_block`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `ethereum_blockchain_height`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1646`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: block height, block production rate, block interval
- Limitations: Chain height is not transaction, evidence, or access-record count.

### `ethereum_blockchain_safe_block`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `ethereum_peer_count`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `4`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: peer count
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `ethereum_peer_count_snap_server`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `ethereum_peer_limit`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `25`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Direct P2P connections; this is not a QBFT quorum measurement.

### `jvm_buffer_pool_capacity_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_buffer_pool_used_buffers`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `1`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_buffer_pool_used_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `1`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_classes_currently_loaded`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `11812`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_classes_loaded_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `11821`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_classes_unloaded_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `9`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_compilation_time_seconds_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `106.732`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_gc_collection_seconds_count`

- Result type: vector
- Labels: __name__, gc, instance, job
- Sample value: `20`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_gc_collection_seconds_sum`

- Result type: vector
- Labels: __name__, gc, instance, job
- Sample value: `1.239`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_committed_bytes`

- Result type: vector
- Labels: __name__, area, instance, job
- Sample value: `76546048`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_init_bytes`

- Result type: vector
- Labels: __name__, area, instance, job
- Sample value: `113246208`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_max_bytes`

- Result type: vector
- Labels: __name__, area, instance, job
- Sample value: `1799356416`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_objects_pending_finalization`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_allocated_bytes_total`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `2035840`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_collection_committed_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `18874368`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_collection_init_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `23068672`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_collection_max_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `-1`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_collection_used_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_committed_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `2555904`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_init_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `2555904`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_max_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `5840896`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_pool_used_bytes`

- Result type: vector
- Labels: __name__, instance, job, pool
- Sample value: `1980544`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_memory_used_bytes`

- Result type: vector
- Labels: __name__, area, instance, job
- Sample value: `51123648`
- Instances (up to 5 sampled series): validator-1:9545, validator-2:9545, validator-4:9545
- Likely dashboard use: JVM memory
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_runtime_info`

- Result type: vector
- Labels: __name__, instance, job, runtime, vendor, version
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_current`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `56`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: thread count
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_daemon`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `15`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_deadlocked`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_deadlocked_monitor`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `0`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_peak`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `57`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_started_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `66`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `jvm_threads_state`

- Result type: vector
- Labels: __name__, instance, job, state
- Sample value: `0`
- Instances (up to 5 sampled series): validator-1:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_cpu_seconds_total`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `140.06`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_max_fds`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1048576`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_open_fds`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `369`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: open file descriptors
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_release`

- Result type: vector
- Labels: __name__, instance, job, version
- Sample value: `1`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_resident_memory_bytes`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `372989952`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: process memory
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_start_time_seconds`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `1785813737.455`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

### `process_virtual_memory_bytes`

- Result type: vector
- Labels: __name__, instance, job
- Sample value: `5953536000`
- Instances (up to 5 sampled series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- Likely dashboard use: Supporting node diagnostics
- Limitations: Metric semantics are limited to the Besu process and labels shown.

## Metrics Required for Dashboard

- **node availability**: confirmed available; metrics: `up`
- **block height**: confirmed available; metrics: `ethereum_blockchain_height`
- **block production rate**: requires derived PromQL; metrics: `ethereum_blockchain_height`; PromQL: `rate(ethereum_blockchain_height[5m])`
- **block interval**: requires derived PromQL; metrics: `ethereum_blockchain_height`; PromQL: `1 / rate(ethereum_blockchain_height[5m])`
- **peer count**: confirmed available; metrics: `ethereum_peer_count`
- **transaction pool**: confirmed available; metrics: `besu_transaction_pool_number_of_transactions`
- **transaction count**: confirmed available; metrics: `besu_blockchain_chain_head_transaction_count`
- **JVM memory**: confirmed available; metrics: `jvm_memory_used_bytes`
- **process memory**: confirmed available; metrics: `process_resident_memory_bytes`
- **CPU**: requires derived PromQL; metrics: `process_cpu_seconds_total`; PromQL: `rate(process_cpu_seconds_total[5m])`
- **thread count**: confirmed available; metrics: `jvm_threads_current`
- **garbage collection**: confirmed available; metrics: `jvm_gc_collection_seconds_count`, `jvm_gc_collection_seconds_sum`
- **open file descriptors**: confirmed available; metrics: `process_open_fds`
- **QBFT or consensus metrics**: partially available; metrics: `besu_executors_bfttimerexecutor_qbft_active_threads_current`
- **RPC metrics**: confirmed available; metrics: `besu_rpc_active_http_connection_count`
- **sync status**: confirmed available; metrics: `besu_synchronizer_in_sync`

QBFT health must be inferred from block progress, validator target availability, and peer connectivity. These indicators are not a direct quorum metric.
