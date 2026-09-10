# ความปลอดภัยของโมดูล Blockchain

นโยบายนี้ครอบคลุม package `0.1.x` และ EvidenceRegistryV3 ของโครงการ
แจ้งช่องโหว่เป็นการส่วนตัวกับผู้ดูแล repository; อย่าเผยแพร่ private keys, credentials หรือข้อมูลโจมตีใน public issue

## แยกหน้าที่ key

Validator 4 keys และ RPC key เป็น node identities; ห้ามนำไปใช้ลงนามธุรกรรมของแอป
Deployer ใช้ deploy, Admin ใช้ grant/revoke, Pauser ใช้ pause/unpause และ Writer ใช้บันทึกรายการ
constructor ให้ admin เป็น Pauser ด้วย; การให้ Pauser ใหม่ไม่ลบสิทธิ์เดิม
Backend runtime ต้องมี Blockchain secret เฉพาะ `BLOCKCHAIN_WRITER_PRIVATE_KEY`
เก็บ admin แยกจาก backend; งานลงนามใหม่ควร inject `TransactionSigner`

## Secret และ backup

`.env.example`/`.env.anvil.example` ต้องมีเพียง placeholder หรือ public config
ห้าม commit keys, `.env`, backup archive/keyfile หรือส่งค่าเหล่านี้ไป frontend/API/log/proof/chat
Git ignore ไม่สามารถลบ secret ที่เคย commit ได้ ต้องตรวจ tracked files, staging และ history แยก
CI ใช้ ephemeral keys ลงไฟล์สิทธิ์ `0600` และลบด้วย `if: always()`
ดู [inventory และ restore](network/besu/docs/backup-recovery.md); เก็บ archive และ recovery key แยกกัน

## RPC และ monitoring

Compose หลัก bind RPC และ Grafana เฉพาะ localhost; validator ไม่มี HTTP/WS RPC
RPC เปิด `ETH`, `NET`, `WEB3`; ไม่เปิด account unlock, admin, debug หรือ consensus management API
ปิด discovery และใช้ static peers; ไม่เปิด wildcard CORS
ค่า Grafana จาก environment ใช้ตอนตั้งต้น; ตรวจบัญชีใน persistent volume แยกจาก `.env`
ก่อนใช้ต่าง host ต้องออกแบบ firewall, TLS, authentication และ secret storage ให้เหมาะสม

## เมื่อ key สูญหายหรือรั่ว

กู้ node key เดิมจาก backup; สร้าง identity เดิมจาก public address ไม่ได้
Writer รั่ว: ใช้ Admin ให้ role แก่ Writer ใหม่แล้วถอน role เดิม พร้อมปรับ runtime อย่างมีแผน
Admin/Pauser รั่ว: ประเมิน role state และย้ายสิทธิ์ผ่านบัญชีที่ยังเชื่อถือได้
ขั้นตอนเหล่านี้สร้างธุรกรรมจริง ต้องบันทึกผลและตรวจ role ภายหลัง ไม่ทำอัตโนมัติระหว่าง audit
ระบบนี้ยังเป็น integration/staging; backup ของ secrets ไม่ใช่หลักฐานว่า chain recovery ผ่านแล้ว
