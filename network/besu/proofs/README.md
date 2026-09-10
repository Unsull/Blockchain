# หลักฐานตรวจสอบธุรกรรม V3

โฟลเดอร์นี้เก็บ JSON/Markdown proof ที่สร้างจาก chain; generated files ถูก Git ignore
proof ใช้ receipt, calldata, event, block inclusion และ contract state ตาม chain/address ที่กำหนด
ใช้ artifact EvidenceRegistryV3 และเก็บ hash/address/opaque references โดยไม่ใส่ private keys/passwords

จาก root ของ blockchain ใช้ `network/besu/scripts/transaction-proof.py`:

- `verify-evidence --tx-hash ...` และ `verify-access --tx-hash ...` อ่านธุรกรรมเดิม ไม่ต้องมี Writer key
- `record-evidence` และ `record-access --evidence-ref ...` ส่งธุรกรรมจริง ต้องมี `WRITER_PRIVATE_KEY` และอนุมัติทดสอบก่อน
- ระบุ `--rpc-url`, `--chain-id 20260720`, `--contract-address`, `--artifact-path` หรือ public environment ที่เกี่ยวข้อง
- ใช้ `--json-output`/`--markdown-output` กำหนดไฟล์ และ `--confirmations` กำหนดความลึก

CLI ไม่โหลด `.env` เอง; อย่าส่ง administrative keys ให้คำสั่ง verify
V3 access proof มี action, occurredAt และ recordedAt; ทั้งสองเวลามีที่มาต่างกัน
proof สะท้อนสถานะและ config ณ เวลาสร้าง ไม่ใช่ใบรับรองทางกฎหมาย
ตรวจ opaque references และข้อมูลที่แชร์ก่อนเผยแพร่; ไม่ใช้ชื่อจริงหรือข้อมูลส่วนบุคคล
อย่าเขียนทับ proof เก่าเพื่อให้ดูเป็นผลจาก deployment ใหม่
