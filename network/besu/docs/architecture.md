# สถาปัตยกรรม Besu QBFT

เครือข่ายใช้ 4 validators และ RPC node แยก 1 ตัวบน Docker host เดียว
Besu pin `26.7.0`; network/chain ID `20260720`; smart contract คือ EvidenceRegistryV3

```text
backend -> RPC (ETH/NET/WEB3) -> validator-1..4 (QBFT)
5 Besu metrics endpoints :9545 -> Prometheus -> Grafana :3001
```

validators ปิด HTTP/WS RPC และไม่ publish host ports
RPC bind `127.0.0.1:${RPC_HTTP_PORT}` (default 8545); discovery ปิดและใช้ static peers
Compose กำหนด IPAM ใน `besu-private` และ mount config/genesis/key แบบ read-only
named volumes เก็บ chain data; data-init containers เตรียม owner ของแต่ละ volume
Prometheus/Grafana มี persistent volumes แยกกัน

QBFT ชุด 4 validators ต้องมี 3 ตัวร่วมทำงานจึงเดินหน้าต่อได้ตามเงื่อนไข consensus
ทน validator หยุด 1 ตัว; หยุด 2 ตัวคาดว่า block production หยุดจนกู้ quorum
target `UP` หรือ peer count เพียงอย่างเดียวไม่ยืนยันว่า validator ลงคะแนนในรอบปัจจุบัน
การวางทุก node บน host เดียวไม่แยกความเสี่ยงจาก host failure
ดู [failure-testing](failure-testing.md) และ [backup-recovery](backup-recovery.md)
