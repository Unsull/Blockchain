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
options: `--scenario-file`, `--output-directory`, `--prometheus-url`, `--rpc-url`, `--chain-id`, `--contract-address`, `--artifact-path`, `--allowed-down-instance`, `--prometheus-step-seconds`
ก่อนรันต้องตรวจ RPC/chain/address/bytecode, Writer role และ Prometheus targets ทั้ง 5
ต้องมีสถานะตรงกับ condition ที่ประกาศ โดย default ต้อง UP ทั้งหมด
observations มี snapshots ก่อน/หลังและ time series ทุก 15 วินาทีระหว่าง measured repetition
ไม่ใช่การสังเกตแยกทุกธุรกรรมอย่างต่อเนื่อง

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
`summary-<run_id>.json`, `network-<run_id>.json` และ
`metrics-timeseries-<run_id>.csv`
เก็บ scenario, repetition, เวลา, experimental condition, ผลรายธุรกรรม, statistics,
Prometheus snapshots และ time series ช่วง measured run ที่ผูกกลับด้วย `run_id`

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

## Research Experiment: 100 Transactions

ไฟล์ `scenarios-research-100.json` แยกจาก default matrix และมี `evidence-c100`
กับ `access-c100` อย่างละ 100 measured transactions, concurrency 100, 1 confirmation
และ 3 repetitions ข้อมูลทั้งหมดเป็น synthetic data ตาม `BenchmarkRunner` ห้ามใช้ production
evidence หรือข้อมูลส่วนบุคคล

100 concurrent workers หมายถึงมี worker ได้พร้อมกันสูงสุด 100 งาน ไม่ได้แปลว่า
100 transactions ถูก broadcast ในขณะเดียวกันพอดี เพราะ writer nonce reservation จะ serialize
ช่วงอ่าน nonce, สร้าง และ broadcast transaction เพื่อรักษาลำดับ nonce

### A. 4/4 Validators Active

ตรวจว่า Prometheus เห็น `validator-1` ถึง `validator-4` และ `rpc-node` เป็น UP ทั้งหมด
แล้วรันจาก repository root:

```bash
python network/besu/scripts/benchmark-transactions.py \
  --scenario-file network/besu/benchmarks/scenarios-research-100.json \
  --output-directory network/besu/benchmarks/results/4v-c100
```

### B. 3/4 Validators Active

เงื่อนไขนี้คือ degraded QBFT ที่ตั้งใจหยุด validator หนึ่งตัวจาก topology 4 validators
ไม่ใช่การสร้าง total 3-node network โดย `validator-1`, `validator-2`, `validator-3` และ
`rpc-node` ต้องยัง UP, Prometheus ต้องยังมี target `validator-4:9545` แต่รายงาน `up=0`
และ block height ต้องยังเพิ่มก่อนเริ่มวัด

หยุดเฉพาะ validator-4 โดยไม่ลบ container volume:

```bash
docker compose --project-directory network/besu \
  --env-file network/besu/.env \
  -f network/besu/docker-compose.yml \
  -f network/besu/docker-compose.monitoring.yml \
  stop validator-4

python network/besu/scripts/benchmark-transactions.py \
  --scenario-file network/besu/benchmarks/scenarios-research-100.json \
  --allowed-down-instance validator-4:9545 \
  --output-directory network/besu/benchmarks/results/3v-c100
```

Benchmark จะ reject หาก validator-4 ยัง UP, target หายไป, node อื่น DOWN หรือ RPC node DOWN
และตรวจ condition นี้ทั้งก่อนและหลัง measured run

กู้คืน validator-4 หลังจบการทดลอง:

```bash
docker compose --project-directory network/besu \
  --env-file network/besu/.env \
  -f network/besu/docker-compose.yml \
  -f network/besu/docker-compose.monitoring.yml \
  up -d validator-4
```

ห้ามใช้ `docker compose down -v`, ห้าม reset chain, ห้ามลบ volumes, ห้ามแก้ nonce
ด้วยมือ และต้องตรวจว่า validator-4 กลับมา UP พร้อม block height เดินต่อหลังการกู้คืน

### วิเคราะห์ Research Dataset

ชุด c100 ไม่ใช่ default c1/c2/c5/c10 matrix จึงใช้ option ที่มีอยู่แล้ว:

```bash
python network/besu/scripts/analyze-benchmark-results.py \
  network/besu/benchmarks/results/4v-c100 \
  --skip-matrix-validation

python network/besu/scripts/analyze-benchmark-results.py \
  network/besu/benchmarks/results/3v-c100 \
  --skip-matrix-validation
```

`run`, `transactions`, `summary` และ aggregate outputs เป็นแหล่งข้อมูล transaction/performance
ส่วน `network` และ `metrics-timeseries` เป็นแหล่งข้อมูล network/resource จาก Prometheus
ที่ step 15 วินาทีตาม scrape interval ปัจจุบัน ค่า `process_cpu_rate` มีหน่วยเป็น CPU cores
จาก `rate(...[5m])` ไม่ใช่เปอร์เซ็นต์ และ labels เช่น JVM `area` ถูกเก็บเป็น JSON ในคอลัมน์
`labels` ของ CSV ส่วน Grafana ใช้สำหรับสำรวจภาพรวม ไม่ใช่หลักฐานยืนยันความสำเร็จของ
specific transaction
