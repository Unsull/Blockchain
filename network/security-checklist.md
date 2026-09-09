# รายการตรวจความปลอดภัยเครือข่าย

- ตรวจ image pin `hyperledger/besu:26.7.0` และ config QBFT/Chain ID `20260720`
- รักษา genesis เดิมและ validator identities ทั้ง 4; แยก RPC node ออกจาก validators
- ตรวจ RPC bind localhost และ namespaces `ETH`, `NET`, `WEB3`; ปิด unlocked accounts
- ตรวจ static peers ตรงกับ public keys และ Compose IPAM
- แยก node, Deployer, Admin, Pauser และ Writer keys; backend ถือเฉพาะ Writer
- ตรวจ Git ignore, tracked/staged files และ history โดยไม่พิมพ์ค่า secret
- ตรวจ Grafana credentials, port `3001`, Prometheus targets และ block progress
- สำรอง keys/config แบบเข้ารหัส แยก recovery key และทดสอบ authentication/checksum
- วางแผน chain-volume snapshot และ restore drill แยกจาก secrets backup
- ก่อนใช้งานจริงตรวจ firewall/TLS, storage, monitoring, backup และ signer บน host เป้าหมาย

ดู [นโยบายโมดูล](../SECURITY.md) และ [คู่มือ backup](besu/docs/backup-recovery.md)
