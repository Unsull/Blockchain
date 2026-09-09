# Monitoring และ Grafana ของ Besu QBFT

Compose หลักรวม Prometheus และ Grafana สำหรับ Besu `26.7.0` ทั้ง 4 validators และ RPC 1 ตัว
Prometheus scrape `:9545` ทุก 15 วินาที; Grafana datasource UID `prometheus`
dashboard UID `besu-qbft-overview` อยู่โฟลเดอร์ **Besu** ชื่อ **Besu QBFT Private Network Overview**

## Ports และการเริ่มระบบ

เริ่มระบบเดิมตาม [operations](operations.md) โดยใช้ Compose หลัก
Grafana: [localhost:3001](http://127.0.0.1:3001/d/besu-qbft-overview), RPC: `127.0.0.1:8545`
Prometheus เข้าถึงใน Docker network ที่ `prometheus:9090`; Compose หลักไม่ publish port นี้ไป host

เมื่อต้องใช้ Prometheus API จาก host สำหรับ benchmark/discovery สามารถใช้ monitoring override
คำสั่งต่อไปนี้เปลี่ยน published ports จึงต้องเลือกใช้ให้ตรงกับ environment:

```bash
docker compose --project-directory network/besu --env-file network/besu/.env -f network/besu/docker-compose.yml -f network/besu/docker-compose.monitoring.yml up -d
```

override เพิ่ม Prometheus ที่ `127.0.0.1:9090` และ Grafana ที่ `127.0.0.1:3000`
Compose merge ports กับไฟล์หลัก จึงยังมี Grafana `3001` ด้วย ไม่ได้ย้าย port หลักไป `3000`
ตรวจรายการจริงด้วย `docker compose ... ps`; ตรวจ config แบบ `--quiet` เพื่อไม่พิมพ์ credentials

## Credentials และ targets

บัญชีเริ่มต้นมาจาก `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD` ใน `.env`
ห้ามใส่ค่าจริงในเอกสาร; ถ้า Grafana volume มีบัญชีแล้ว การแก้ environment ไม่ใช่การเปลี่ยน password ของบัญชีเดิม
ตรวจหรือเปลี่ยนผ่านกระบวนการดูแล Grafana ที่เหมาะสม

เมื่อเปิด Prometheus host port แล้ว ดู `/targets` หรือ `/api/v1/targets`
คาดว่า `validator-1:9545` ถึง `validator-4:9545` และ `rpc-node:9545` เป็น `UP`
UP หมายถึง scrape สำเร็จ ไม่ได้พิสูจน์ consensus participation
`scripts/validate-monitoring-dashboard.py` ตรวจ dashboard/queries ผ่าน APIs; ใช้ `--help`
และกำหนด `--grafana-url http://127.0.0.1:3001` ให้ตรง port หลัก

## ความหมายของ panels

| กลุ่ม | สิ่งที่แสดงและข้อจำกัด |
| --- | --- |
| Network Overview | 5 node targets, 4 validator targets, RPC state, block height, peers, sync |
| Blockchain Activity | block rate/interval จากช่วง 5 นาที, tx pool, transactions ใน head block, HTTP connections |
| Node Resources | JVM/process memory, CPU cores ที่ process ใช้, threads, file descriptors, GC |
| Consensus and Network Health | ความต่าง block height, peers, availability, inferred stall และ QBFT timer threads |
| Monitoring Health | scrape state และ memory เทียบ threshold 1.5 GB; alert มี `for` duration แยก |

stall ใช้ RPC height ที่ไม่เพิ่มในช่วง 1 นาที ต้องดู target health/sample gaps/startup ประกอบ
block-height divergence คือ max−min ของ nodes ที่มองเห็น; ค่า 1 อาจเกิดช่วง scrape คาบเกี่ยว
peer count ไม่ใช่ quorum; QBFT timer threads ไม่ใช่จำนวน votes; CPU ไม่ใช่เปอร์เซ็นต์ของทั้ง host
transaction count ใน head block ไม่ใช่ยอดธุรกรรมสะสม; tx pool ไม่ใช่ธุรกรรมยืนยันแล้ว
metrics ไม่บอกจำนวน evidence/access ของ V3 และ Grafana ไม่ใช่ proof ของธุรกรรมรายรายการ

## Export และข้อมูลอ้างอิง

export panel/data ผ่าน Grafana; image rendering ต้องมี renderer ที่รองรับใน installation
Prometheus query API เก็บ JSON ได้ เช่น `ethereum_blockchain_height{job="besu"}`
ระบุ UTC timestamp, query/range/step, config และ version เมื่อใช้ในรายงานวิจัย
ดู [metric inventory](../monitoring/discovered-metrics.md) ซึ่งเป็น snapshot เก่า ไม่ใช่สถานะ live
ตรวจ proof ของธุรกรรมด้วย [transaction proofs](../proofs/README.md)

หยุดด้วย Compose configuration ชุดเดียวกับที่เริ่มและใช้ `down` โดยไม่ใส่ `-v`
ระบบเป็น integration/staging: ไม่มี direct quorum/vote metrics, host monitoring ครบทุกด้าน หรือ external TLS/authentication
