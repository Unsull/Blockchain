# สำรอง Secrets และกู้คืนเครือข่าย

การสำรอง secret/config ช่วยกู้ identities และการตั้งค่า แต่ **ไม่ใช่การสำรอง chain state**
ถ้า chain volumes ทุกชุดสูญหาย จะกู้ธุรกรรมและ contract state เดิมจาก keys/genesis เพียงอย่างเดียวไม่ได้

## Inventory ที่ต้องสำรอง

paths ต่อไปนี้อ้างจาก parent `CapstoneProject`:

| รายการ | Path |
| --- | --- |
| Validator 1–4 keys (4 ไฟล์) | `blockchain/network/besu/keys/validator-1/key` ถึง `validator-4/key` |
| RPC identity | `blockchain/network/besu/keys/rpc-node/key` |
| Administrative environment | `blockchain/.env`, `blockchain/network/besu/.env` |
| Backend runtime environment | `backend/.env` |
| Genesis เดิม | `blockchain/network/besu/genesis/genesis.json` |
| Static peers | `blockchain/network/besu/build/static-nodes.json` |

รวม inventory หลัก 10 ไฟล์; สำรอง `key.pub`/`address` ที่มีใน canonical key directories เพิ่มด้วย
เพราะ validator validation และ static-peer renderer ใช้ public metadata เหล่านี้
`backend/.env` ที่สำรองทั้งไฟล์อาจมี secrets ของระบบอื่นด้วย จึงต้องปกป้องทั้ง archive
ไม่จำเป็นต้องสำรอง generated key copies ใน `build/keys/` ซ้ำ แต่ไม่ลบทิ้งเพียงเพราะเป็นสำเนา

Git เก็บ `qbftConfigFile.json`, node configs, Compose, monitoring, contract, ABI fixture และ V3 manifest
ให้เก็บ commit IDs และสำเนา repositories/submodules ที่เข้าถึงได้สำหรับ recovery ระยะยาว

## Backup ที่สร้างวันที่ 9 กันยายน 2026

สร้าง inventory หลัก 10 ไฟล์และ public metadata 5 ไฟล์ รวม 15 ไฟล์:

- Archive: `C:\Users\kiadt\Documents\BlockchainBackups\20260909T015158Z\blockchain-secrets.bcbk`
- Recovery key: `C:\Users\kiadt\.blockchain-backup-keys\20260909T015158Z\blockchain-backup.key`
- ในโฟลเดอร์ archive มี `backup_restore.py`, `backup-report.json`, `SHA256SUMS.txt`
- วิธีเข้ารหัส: AES-256-GCM, random key 32 bytes, nonce 12 bytes, authentication tag 16 bytes
- รูปแบบ `BCBKGCM1`: header 8 bytes + nonce + tag + ciphertext ของ ZIP; header ใช้เป็น authenticated data
- Windows ACL อนุญาตเฉพาะบัญชีเจ้าของ `kiadt` และ SYSTEM ที่ archive/key directories
- ZIP plaintext สร้างใน memory; ไม่เขียน temporary plaintext archive ลง disk
- ผ่านการถอดรหัสเทียบต้นฉบับทุกไฟล์และ SHA-256; key ผิดหรือ ciphertext ถูกแก้ไขต้องถูกปฏิเสธ

ทดสอบ restore ลง disk ในโฟลเดอร์ที่จำกัดสิทธิ์แล้ว เทียบทั้ง 15 ไฟล์กับต้นฉบับผ่าน และลบเฉพาะสำเนาทดสอบเรียบร้อย

ไฟล์กุญแจเป็น raw encryption key ไม่ได้ตั้ง password ให้ archive
ห้ามเปิดเนื้อหากุญแจใน chat/log และต้องเก็บไฟล์นี้ใน password manager หรือสื่อปลอดภัยแยกจาก archive
สองโฟลเดอร์บนเครื่องเดียวกันยังไม่ใช่ backup คนละสื่อ ต้องคัดลอกไปสื่อแยกเมื่อจัดเตรียมแล้ว

## ตรวจ checksum และ authentication

SHA-256 ของ archive ชุดนี้:

```text
34de5578f03e89d3dada5124d1d5251af054377847c565fa79b4878b170ee4c8
```

ตัวอย่าง PowerShell (ใช้ Python ที่มี `pycryptodome`; Windows restore ต้องมี `pywin32`):

```powershell
$backupDir = 'C:\Users\kiadt\Documents\BlockchainBackups\20260909T015158Z'
$keyPath = 'C:\Users\kiadt\.blockchain-backup-keys\20260909T015158Z\blockchain-backup.key'
Get-FileHash -Algorithm SHA256 -LiteralPath "$backupDir\blockchain-secrets.bcbk"
python "$backupDir\backup_restore.py" verify --archive "$backupDir\blockchain-secrets.bcbk" --key-file $keyPath
```

เทียบ checksum กับ `SHA256SUMS.txt`/ค่าที่บันทึกไว้ จากนั้น `verify` ตรวจ GCM tag และ SHA-256 รายไฟล์ใน encrypted inventory
checksum อย่างเดียวไม่ทดแทน authentication ด้วย GCM

## Restore ไปโฟลเดอร์ใหม่ก่อน

```powershell
python "$backupDir\backup_restore.py" restore --archive "$backupDir\blockchain-secrets.bcbk" --key-file $keyPath --destination 'C:\Users\kiadt\Documents\BlockchainRestore-Review'
```

ปลายทางต้องยังไม่มีอยู่; สคริปต์ไม่เขียนทับระบบเดิม และตรวจ checksum หลังเขียนทุกไฟล์
โครงสร้างที่ได้เป็น `blockchain/...` และ `backend/.env` ตาม parent repository
สคริปต์ Windows ใช้ ACL ของบัญชี `kiadt`; ถ้ากู้บน Windows เครื่องอื่นให้ผู้ดูแลปรับชื่อบัญชีใน `protect()` ก่อน
บน Linux/macOS ใช้ directory mode `0700` และ file mode `0600`
ตรวจสิทธิ์ filesystem ของ node keys ให้สอดคล้องกับ Besu UID/GID ก่อนนำไป mount ใช้งาน

เมื่อทบทวนไฟล์กู้คืนแล้ว จึงวางแผนหยุดบริการที่เกี่ยวข้องและนำไฟล์กลับ path เดิมอย่างควบคุม
ไม่คัดลอก `.env` ทับโดยไม่ตรวจ config และไม่เปลี่ยน genesis ที่ volumes เดิมใช้งาน
ตรวจ keys/public metadata/genesis/static peer mapping แล้วจึงเริ่ม node และตรวจ sync/peers/block progress
ใช้ `validate-generated-network.py`, `health-check.py` และ `scripts/verify_deployment.py` ตามคู่มือ operations
ตรวจ contract bytecode/address และ role state ก่อนเปิด backend writes
smoke test เป็นธุรกรรมจริง ให้ทำเมื่ออนุมัติการทดสอบเท่านั้น

## Chain data และขอบเขตการทดสอบ

named volumes คือ `evidence-besu-qbft_validator-1-data` ถึง `validator-4-data`
และ `evidence-besu-qbft_rpc-node-data`; monitoring มี `prometheus-data` และ `grafana-data` ภายใต้ project prefix เดียวกัน
ต้องวางแผน consistent snapshots/restore แยก; ห้ามถือการ copy live database แบบไม่ประสานงานว่า consistent
ทดสอบการกู้ RPC/validator บนสำเนา environment ที่แยกไว้ พร้อม keys/genesis เดิมและข้อมูล chain ที่เพียงพอ
รอบนี้ตรวจ backup secrets/config; ไม่ reset network, ไม่ snapshot/delete volumes และไม่อ้างว่า full-chain recovery ผ่าน
