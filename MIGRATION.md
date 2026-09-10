# การย้าย integration มาใช้ EvidenceRegistryV3

runtime ปัจจุบันใช้ V3 เท่านั้น ไม่มี deployment target หรือ contract รุ่นก่อนหน้าใน workflow ปัจจุบัน
เอกสารนี้อธิบายการปรับ API ไม่ใช่คำสั่ง redeploy chain ที่ใช้งานอยู่

## รูปแบบข้อมูลปัจจุบัน

- `recordEvidence(evidenceRef, evidenceHash, uploaderRef)` ใช้ `bytes32` ที่ไม่เป็นศูนย์
- `recordAccess(evidenceRef, officerRef, accessSessionRef, action, occurredAt)` ใช้ `VIEW=0`, `DOWNLOAD=1`
- `occurredAt` คือเวลาจาก backend; `recordedAt` คือเวลาบันทึกบน chain
- ใช้ชื่อ `evidenceHash` ตาม V3 ไม่ใช้ `watermarkHash` หรือ `staticHash` เป็น field ปัจจุบัน
- อ่าน access ตาม session ด้วย `getAccessBySession`; ไม่มี API คืน array logs แบบไม่จำกัด
- bytes32 ที่ client ส่งออกเป็น lowercase hex มี prefix `0x`

## Backend integration

ใช้ `blockchain_client.BlockchainClient` กับ settings และ signer ที่ inject เข้ามา
การส่งจาก unlocked account และ FastAPI demo ไม่ใช่ API ของโมดูลนี้
ตัวอย่าง FastAPI เก่าถูกลบเพราะไม่มี consumer; authentication และ mapping ตัวตนอยู่ใน backend
`signer_private_key` ยังรองรับเพื่อ compatibility แต่ integration ใหม่ควรใช้ `TransactionSigner`
API queries ตรวจ connection, chain ID และ bytecode ก่อนอ่าน state

## Artifact และ state

ใช้ ABI/artifact V3 และ manifest `network/besu/deployments/20260720/EvidenceRegistryV3.json`
contract เป็น immutable; เปลี่ยน schema ในอนาคตต้องมีแผน version/deployment แยก
หากต้องตรวจธุรกรรมจากระบบเก่า ให้รักษา artifact/address/chain snapshot ของระบบนั้นไว้นอก active runtime
ห้ามแปลง state เก่าเป็น V3 โดยแก้ manifest อย่างเดียว และไม่ reset volumes เพื่อแก้ config ผิด
