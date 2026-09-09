# เครือข่าย Blockchain

เครือข่ายที่ดูแลในโครงการอยู่ที่ [besu/](besu/README.md): Hyperledger Besu `26.7.0`,
QBFT 4 validators + 1 RPC, Chain ID `20260720`, contract EvidenceRegistryV3
ตัวอย่าง genesis/static peers เก่าที่ระดับโฟลเดอร์นี้ถูกลบแล้ว เพราะไม่มี consumer ใน workflow ปัจจุบัน

ใช้ [operations](besu/docs/operations.md) สำหรับเริ่ม/หยุดระบบเดิมและขั้นตอนสร้าง chain ใหม่ที่แยกไว้ชัดเจน
ใช้ [backup-recovery](besu/docs/backup-recovery.md) สำหรับ keys, recovery config และข้อจำกัด chain volumes

RPC เปิดเฉพาะ `ETH`, `NET`, `WEB3` บน localhost; validators ปิด HTTP/WS RPC
Prometheus เก็บ metrics ของ 5 nodes และ Grafana ของ Compose หลักอยู่ที่ port `3001`
Anvil เป็นทางเลือกทดสอบใน environment แยก ไม่ใช่ genesis หรือ consensus ของ Besu ปัจจุบัน
