# ความปลอดภัย Besu network

config ปัจจุบัน bind RPC ที่ localhost, ปิด validator HTTP/WS RPC และเปิด `ETH`, `NET`, `WEB3` ที่ RPC node
ปิด discovery, ใช้ static peers, ไม่เปิด wildcard CORS หรือ unlocked account API
keys/config ถูก mount read-only; data อยู่ Docker named volumes

node keys, `.env`, generated build, logs และข้อมูล runtime ถูก Git ignore ตาม `.gitignore`
ห้ามใช้ validator/RPC identity เป็น Deployer/Admin/Pauser/Writer
backend มีเฉพาะ Writer secret; admin ควบคุม role และไม่ใช้เขียนหลักฐานประจำวัน
เก็บ secret ผ่าน controlled environment/secret manager ไม่ผ่าน command-line argument หรือ shell tracing

Grafana หลักอยู่ localhost:3001; ตรวจ `GRAFANA_ADMIN_USER`/`GRAFANA_ADMIN_PASSWORD`
และบัญชีจริงใน Grafana volume แยกกัน ห้าม commit password
monitoring override เปิด Prometheus localhost:9090 และเพิ่ม Grafana localhost:3000
ไม่ใช่ค่า port หลักของ stack

สำรอง canonical keys, environment และ recovery config แบบเข้ารหัสตาม [คู่มือ](backup-recovery.md)
manifest/ABI เป็น public metadata แต่ archive ที่รวม secrets ต้องจำกัดสิทธิ์
ก่อนเปิดใช้ต่าง host ต้องออกแบบ TLS/firewall/authentication และทดสอบ upgrade ด้วย environment แยก
ดู [นโยบายโมดูล](../../../SECURITY.md)
