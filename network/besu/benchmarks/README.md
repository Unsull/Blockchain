# Benchmark ของ EvidenceRegistryV3

เครื่องมือวัด application transaction performance บน Besu QBFT 4 validators + 1 RPC
Chain ID `20260720` บน Docker host เดียว พร้อม Prometheus/Grafana
benchmark **ส่งธุรกรรมจริง** ใช้เฉพาะ environment และช่วงเวลาทดสอบที่อนุมัติแล้ว
ผลขึ้นกับ CPU, memory, disk, Docker scheduling, block timing และภาระงานของเครื่อง
ไม่ใช่ขีดความสามารถสูงสุดของ Besu หรือผลจากระบบกระจายหลาย host

## Workloads และ matrix

`recordEvidence` สร้าง evidenceRef/evidenceHash/uploaderRef สังเคราะห์ไม่ใช้ข้อมูลส่วนบุคคล
`recordAccess` ใช้ evidence ที่เตรียมไว้ก่อนวัด, officerRef/sessionRef สังเคราะห์,
action และ `occurredAt` ตาม API V3; ไม่นับธุรกรรมเตรียม evidence ใน access latency/throughput

แหล่งจริงคือ `scenarios.json`:

| Scenarios | Operation | Transactions/run | Concurrency | Confirmations | Repetitions |
| --- | --- | ---: | --- | ---: | ---: |
| evidence-c1/c2/c5/c10 | recordEvidence | 20 | 1, 2, 5, 10 | 1 | 3 |
| access-c1/c2/c5/c10 | recordAccess | 20 | 1, 2, 5, 10 | 1 | 3 |

รวม 24 measured runs (480 measured transactions เมื่อรันครบ) และมี access setup transactions เพิ่มต่างหาก
concurrency คือจำนวนงานพร้อมกัน ไม่ใช่จำนวนธุรกรรมรวม ผลรายรายการเรียงตาม sequence แม้เสร็จไม่พร้อมกัน

## Environment และคำสั่ง

ใช้ Python dependencies ตาม root `pyproject.toml`
ต้องมี `RPC_URL`, `CHAIN_ID`, `CONTRACT_ADDRESS`, `WRITER_PRIVATE_KEY` ผ่าน environment ที่ควบคุมสิทธิ์
optional `ARTIFACT_PATH` และ `PROMETHEUS_URL`; CLI ไม่โหลด `.env` เอง
อย่าส่ง private key เป็น command-line argument หรือบันทึกลง scenarios/results
Prometheus default `http://127.0.0.1:9090` ต้องเปิด monitoring override หรือกำหนด endpoint ที่เข้าถึงได้
Grafana ของ Compose หลักอยู่ `http://127.0.0.1:3001`

จาก root ของ blockchain หลังอนุมัติทดสอบ:

```bash
python network/besu/scripts/benchmark-transactions.py --scenario evidence-c1
```

เริ่ม baseline ก่อน แล้วเพิ่ม concurrency 1 → 2 → 5 → 10 จึงรันครบ matrix
ไม่ระบุ `--scenario` จะเลือกทั้งหมด; ระบุซ้ำเพื่อเลือกหลาย scenario ได้
options: `--scenario-file`, `--output-directory`, `--prometheus-url`, `--rpc-url`, `--chain-id`, `--contract-address`, `--artifact-path`
ก่อนรันต้องตรวจ RPC/chain/address/bytecode, Writer role และ Prometheus 5 targets UP
observations ถูกเก็บก่อนและหลังแต่ละ measured repetition ไม่ใช่การสังเกตทุกธุรกรรมต่อเนื่อง

## Metrics และวิธีตีความ

- Successful throughput = จำนวน measured transactions สำเร็จ / ระยะเวลา run (tx/s)
- success/failure rate ใช้ผล measured transactions ทั้งหมด; failure ไม่ถูกทิ้งเงียบ
- latency min/mean/P50/P95/P99/max ใช้รายการสำเร็จและเป็น end-to-end client time
- gas จาก receipt ของรายการสำเร็จ ไม่ใช่ค่าใช้จ่ายเงินจริงของ private chain
- block distribution ดู first/last/unique blocks และ transactions ต่อ block ที่ใช้
- failure เก็บชนิดข้อผิดพลาดและข้อความผ่านการ sanitization พร้อม sequence/timestamps

client results เป็นแหล่ง latency/throughput/hash/gas/confirmations; Prometheus เป็นบริบท availability,
sync, peer count, chain progress, pool, memory, CPU และ RPC connections
head transaction count ไม่ใช่ยอด application transactions สะสม และ scrape ทุก 15 วินาทีอาจพลาดเหตุการณ์ใน run สั้น
ตรวจ targets ก่อนและหลังไม่ได้พิสูจน์ว่าไม่มี downtime ระหว่างสอง snapshots

## Output และการวิเคราะห์

default output `network/besu/benchmarks/results/` ถูก Git ignore
แต่ละ repetition มี `run-<run_id>.json`, `transactions-<run_id>.csv`,
`summary-<run_id>.json`, `network-<run_id>.json`
เก็บ scenario, repetition, เวลา, ผลรายธุรกรรม, statistics และ Prometheus snapshots ที่ผูก run_id

วิเคราะห์ผลเดิมโดยไม่ส่งธุรกรรมใหม่:

```bash
python network/besu/scripts/analyze-benchmark-results.py network/besu/benchmarks/results/<matrix-directory>
```

ผลคือ `analysis/aggregate.csv`, `analysis/aggregate.json`, `analysis/benchmark-report.md`
เปรียบเทียบ concurrency กับ throughput/latency/failure, gas ของสอง operations และ network/resource observations
รายงานทุก repetition ที่ใช้ได้; ระบุเหตุผลเมื่อไม่ใช้ run ใด ไม่เลือกเฉพาะค่าที่เร็วที่สุด
TPS สูงสุดที่เห็นใน matrix ไม่ใช่การพิสูจน์ maximum capacity
เก็บ UTC/config/version/hardware และข้อจำกัด single-host คู่กับผล

ทดสอบ unit/lint/type checks ก่อนรันจริงตาม README หลัก
ห้ามนำ `.env`, private keys หรือข้อมูลคดีจริงใส่ผลลัพธ์; ตรวจ sanitization ก่อนแชร์
เก็บ source/scenario/methodology ใน Git ส่วนผลวัดและรายงาน generated เก็บตามนโยบายข้อมูลการทดลอง
ไฟล์ผลเก่าเป็นหลักฐานตามเวลาที่วัด ไม่ปรับตัวเลขให้เป็นผลของ network ปัจจุบัน
