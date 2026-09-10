# เครือข่าย Besu QBFT

ใช้ Hyperledger Besu `26.7.0`, Chain ID `20260720`, QBFT 4 validators + 1 RPC
contract ปัจจุบันคือ EvidenceRegistryV3 ดู manifest ใน `deployments/20260720/EvidenceRegistryV3.json`
Compose รวม Prometheus และ Grafana พร้อม named volumes สำหรับ chain และ monitoring

## เริ่มระบบเดิม

จาก root ของ blockchain ใน Bash environment ที่มี Python dependencies:

```bash
bash network/besu/scripts/start-network.sh
python network/besu/scripts/health-check.py --expected-chain-id 20260720
docker compose --project-directory network/besu ps
```

สคริปต์โหลด `network/besu/.env` และใช้ genesis/keys เดิม
อย่ารัน generate/reset หรือคัดลอก `.env.example` ทับระบบที่มีข้อมูลอยู่
RPC หลักอยู่ `http://127.0.0.1:8545`; Grafana อยู่ `http://127.0.0.1:3001`
Prometheus ไม่ publish host port ใน Compose หลัก; ดู monitoring guide เมื่อต้องเปิด port สำหรับงานวิเคราะห์

## โครงสร้าง

```text
backend / blockchain_client -> rpc-node -> validator-1..4 (QBFT)
                               metrics ของทั้ง 5 nodes -> Prometheus -> Grafana
```

Validator ปิด HTTP/WS RPC; RPC เปิดเฉพาะ `ETH`, `NET`, `WEB3`
Compose mount `keys/<node>/key`, `genesis/genesis.json`, `build/static-nodes.json` และ `nodes/<node>/config.toml`
static peers เป็น validator IPs ที่กำหนดใน Compose IPAM; แก้ IP ไม่จำเป็นต้องสร้าง keys ใหม่
chain state อยู่ใน named volumes ไม่ใช่ `nodes/*/data/.gitkeep`

## คู่มือ

- [Operations: run/deploy/test](docs/operations.md)
- [Architecture](docs/architecture.md)
- [Monitoring และ Grafana](docs/monitoring-dashboard.md)
- [Secrets backup และ recovery](docs/backup-recovery.md)
- [Failure tests](docs/failure-testing.md)
- [Security](docs/security.md)
- [Benchmark](benchmarks/README.md) และ [transaction proofs](proofs/README.md)

ระบบนี้ใช้สำหรับ integration/staging; ต้องทดสอบ recovery, host security และ signer ก่อนอ้างความพร้อม production
