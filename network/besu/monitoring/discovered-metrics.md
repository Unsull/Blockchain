# รายการ Prometheus metrics ที่ตรวจพบใน Besu 26.7.0

รายงานนี้เป็น snapshot วันที่ 4 สิงหาคม 2026 ตาม timestamp เดิม ไม่ใช่ผลตรวจ live ของวันที่ปรับเอกสาร
เก็บตัวเลข/metric names ไว้เพื่ออ้างอิงและไม่ตีความว่าเป็น evidence/access totals ของ V3
ดู [คู่มือ monitoring](../docs/monitoring-dashboard.md) สำหรับ Compose หลักและ Grafana port 3001

## Environment ที่ตรวจในอดีต

- รุ่น Besu: 26.7.0
- จำนวน nodes: 5
- จำนวน validators: 4
- จำนวน RPC nodes: 1
- รอบ scrape ของ Prometheus: 15s
- เวลาตรวจ (UTC): 2026-08-04T03:25:20.459293+00:00

## สถานะ targets ณ เวลาตรวจ

| Instance | สถานะ | Scrape ล่าสุด | ระยะเวลา (วินาที) | ข้อผิดพลาดล่าสุด |
| --- | --- | --- | ---: | --- |
| rpc-node:9545 | up | 2026-08-04T03:25:07.691307881Z | 0.042897341 | - |
| validator-1:9545 | up | 2026-08-04T03:25:10.514261779Z | 0.034348074 | - |
| validator-2:9545 | up | 2026-08-04T03:25:10.016033724Z | 0.039937967 | - |
| validator-3:9545 | up | 2026-08-04T03:25:13.201035221Z | 0.025018897 | - |
| validator-4:9545 | up | 2026-08-04T03:25:07.991251577Z | 0.029311279 | - |

## Metrics ที่พบ

### `besu_bal_blocks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_block_processing_conflicted_transactions_counter_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_block_processing_parallelized_transactions_counter_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_block_processing_state_root_calculation_duration_seconds`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, quantile
- ค่าตัวอย่าง: `0.000111541`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_block_processing_state_root_calculation_duration_seconds_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `52`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_block_processing_state_root_calculation_duration_seconds_sum`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0.010140167000000002`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_chain_head_gas_limit`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `9007199254740991`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_chain_head_gas_used`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_chain_head_gas_used_counter_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_chain_head_timestamp`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1785813907`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_chain_head_transaction_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: จำนวนธุรกรรมใน head block
- ข้อจำกัด: อธิบายธุรกรรมใน head block ไม่ใช่จำนวนหลักฐานของ application

### `besu_blockchain_chain_head_transaction_count_counter_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: อธิบายธุรกรรมใน head block ไม่ใช่จำนวนหลักฐานของ application

### `besu_blockchain_difficulty`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1647`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_account_flat_database_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_account_missing_flat_database_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_account_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_storagevalue_flat_database_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_storagevalue_missing_flat_database_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_blockchain_get_storagevalue_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_bfttimerexecutor_qbft_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: metrics ของ QBFT/consensus
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_bfttimerexecutor_qbft_completed_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `49`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_bfttimerexecutor_qbft_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_bfttimerexecutor_qbft_queue_length_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `3`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_bfttimerexecutor_qbft_rejected_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_bfttimerexecutor_qbft_submitted_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `52`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: บอกกิจกรรม executor เท่านั้น ไม่แสดง votes หรือ quorum ของ validators

### `besu_executors_ethscheduler_blockcreation_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_blockcreation_completed_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `14`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_blockcreation_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `2`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_blockcreation_queue_length_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_blockcreation_rejected_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_blockcreation_submitted_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `14`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_chaindatapruner_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_chaindatapruner_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_computation_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_computation_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_services_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_services_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `3`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_timer_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_timer_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_completed_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_dropped_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_queue_length_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_rejected_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_transactions_submitted_tasks_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_workers_active_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_executors_ethscheduler_workers_pool_size_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `8`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_network_vertx_eventloop_pending_tasks`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_network_vertx_worker_pool_completed_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, poolName, poolType
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_network_vertx_worker_pool_rejected_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, poolName, poolType
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_network_vertx_worker_pool_submitted_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, poolName, poolType
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_peers_connected_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `4`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_disconnected_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, disconnectReason, initiator, instance, job
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-2:9545, validator-3:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_inflight_request_gauge`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, taskName
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_peer_count_by_client`

- ชนิดผลลัพธ์: vector
- Labels: __name__, client, instance, job
- ค่าตัวอย่าง: `4`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_pending_peer_requests_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_request_time`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, quantile, taskName
- ค่าตัวอย่าง: `0.004526458`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-2:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_request_time_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, taskName
- ค่าตัวอย่าง: `5`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_peers_request_time_sum`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, taskName
- ค่าตัวอย่าง: `0.45808915600000005`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `besu_rpc_active_http_connection_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545
- การใช้งานใน dashboard: metrics ของ RPC
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_rpc_request_time`

- ชนิดผลลัพธ์: vector
- Labels: none
- ค่าตัวอย่าง: `no sample`
- Instances (ตัวอย่างไม่เกิน 5 series): none in bounded sample
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_rpc_request_time_count`

- ชนิดผลลัพธ์: vector
- Labels: none
- ค่าตัวอย่าง: `no sample`
- Instances (ตัวอย่างไม่เกิน 5 series): none in bounded sample
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_rpc_request_time_sum`

- ชนิดผลลัพธ์: vector
- Labels: none
- ค่าตัวอย่าง: `no sample`
- Instances (ตัวอย่างไม่เกิน 5 series): none in bounded sample
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_chain_download_pipeline_processed_total`

- ชนิดผลลัพธ์: vector
- Labels: none
- ค่าตัวอย่าง: `no sample`
- Instances (ตัวอย่างไม่เกิน 5 series): none in bounded sample
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_chain_download_pipeline_restarts_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, reason
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_in_sync`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: สถานะ sync
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_sync_duration_bucket`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, le, name
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_sync_duration_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, name
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_sync_duration_sum`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, name
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_task`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, quantile, taskName
- ค่าตัวอย่าง: `0.000451426`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_task_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, taskName
- ค่าตัวอย่าง: `9`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_synchronizer_task_sum`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, taskName
- ค่าตัวอย่าง: `0.093371647`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_blob_cache_size`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_blob_map_size`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_messages_expired_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, message
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_number_of_transactions`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, layer
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: pool ธุรกรรมรอประมวลผล
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_number_of_transactions_by_type`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, layer, type
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_space_used`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, layer
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `besu_transaction_pool_unique_senders`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, layer
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `ethereum_best_known_block_number`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1646`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `ethereum_blockchain_finalized_block`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `ethereum_blockchain_height`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1646`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ความสูง block, อัตราสร้าง block, ช่วงเวลาระหว่าง blocks
- ข้อจำกัด: ความสูง chain ไม่ใช่จำนวนธุรกรรม evidence หรือ access

### `ethereum_blockchain_safe_block`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `ethereum_peer_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `4`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: จำนวน peers
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `ethereum_peer_count_snap_server`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `ethereum_peer_limit`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `25`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: จำนวนการเชื่อมต่อ P2P โดยตรง ไม่ใช่ค่า QBFT quorum

### `jvm_buffer_pool_capacity_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_buffer_pool_used_buffers`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_buffer_pool_used_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_classes_currently_loaded`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `11812`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_classes_loaded_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `11821`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_classes_unloaded_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `9`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_compilation_time_seconds_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `106.732`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_gc_collection_seconds_count`

- ชนิดผลลัพธ์: vector
- Labels: __name__, gc, instance, job
- ค่าตัวอย่าง: `20`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_gc_collection_seconds_sum`

- ชนิดผลลัพธ์: vector
- Labels: __name__, gc, instance, job
- ค่าตัวอย่าง: `1.239`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_committed_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, area, instance, job
- ค่าตัวอย่าง: `76546048`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_init_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, area, instance, job
- ค่าตัวอย่าง: `113246208`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_max_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, area, instance, job
- ค่าตัวอย่าง: `1799356416`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_objects_pending_finalization`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_allocated_bytes_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `2035840`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_collection_committed_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `18874368`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_collection_init_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `23068672`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_collection_max_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `-1`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_collection_used_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_committed_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `2555904`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_init_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `2555904`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_max_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `5840896`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_pool_used_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, pool
- ค่าตัวอย่าง: `1980544`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_memory_used_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, area, instance, job
- ค่าตัวอย่าง: `51123648`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545, validator-2:9545, validator-4:9545
- การใช้งานใน dashboard: หน่วยความจำ JVM
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_runtime_info`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, runtime, vendor, version
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_current`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `56`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: จำนวน threads
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_daemon`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `15`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_deadlocked`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_deadlocked_monitor`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_peak`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `57`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_started_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `66`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `jvm_threads_state`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, state
- ค่าตัวอย่าง: `0`
- Instances (ตัวอย่างไม่เกิน 5 series): validator-1:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_cpu_seconds_total`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `140.06`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_max_fds`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1048576`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_open_fds`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `369`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: จำนวน file descriptors ที่เปิด
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_release`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job, version
- ค่าตัวอย่าง: `1`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_resident_memory_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `372989952`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: หน่วยความจำ process
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_start_time_seconds`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `1785813737.455`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

### `process_virtual_memory_bytes`

- ชนิดผลลัพธ์: vector
- Labels: __name__, instance, job
- ค่าตัวอย่าง: `5953536000`
- Instances (ตัวอย่างไม่เกิน 5 series): rpc-node:9545, validator-1:9545, validator-2:9545, validator-3:9545, validator-4:9545
- การใช้งานใน dashboard: ใช้ประกอบการวิเคราะห์ node
- ข้อจำกัด: ความหมายจำกัดอยู่ที่ Besu process และ labels ที่แสดง

## Metrics ที่ dashboard ต้องใช้

- **ความพร้อมใช้งานของ nodes**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `up`
- **ความสูง block**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `ethereum_blockchain_height`
- **อัตราสร้าง block**: ต้องคำนวณผ่าน PromQL; metrics: `ethereum_blockchain_height`; PromQL: `rate(ethereum_blockchain_height[5m])`
- **ช่วงเวลาระหว่าง blocks**: ต้องคำนวณผ่าน PromQL; metrics: `ethereum_blockchain_height`; PromQL: `1 / rate(ethereum_blockchain_height[5m])`
- **จำนวน peers**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `ethereum_peer_count`
- **pool ธุรกรรมรอประมวลผล**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `besu_transaction_pool_number_of_transactions`
- **จำนวนธุรกรรมใน head block**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `besu_blockchain_chain_head_transaction_count`
- **หน่วยความจำ JVM**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `jvm_memory_used_bytes`
- **หน่วยความจำ process**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `process_resident_memory_bytes`
- **CPU**: ต้องคำนวณผ่าน PromQL; metrics: `process_cpu_seconds_total`; PromQL: `rate(process_cpu_seconds_total[5m])`
- **จำนวน threads**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `jvm_threads_current`
- **การเก็บคืนหน่วยความจำ**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `jvm_gc_collection_seconds_count`, `jvm_gc_collection_seconds_sum`
- **จำนวน file descriptors ที่เปิด**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `process_open_fds`
- **metrics ของ QBFT/consensus**: พบข้อมูลบางส่วน; metrics: `besu_executors_bfttimerexecutor_qbft_active_threads_current`
- **metrics ของ RPC**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `besu_rpc_active_http_connection_count`
- **สถานะ sync**: ตรวจพบ ณ เวลาที่เก็บ snapshot; metrics: `besu_synchronizer_in_sync`

สุขภาพ QBFT ต้องประเมินร่วมจาก block progress, target availability และ peer connectivity; ไม่ใช่ direct quorum metric
