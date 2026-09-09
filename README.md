# โมดูล Blockchain — EvidenceRegistryV3

โมดูลบันทึกและตรวจสอบหลักฐานบน private EVM โดยใช้ `EvidenceRegistryV3` เท่านั้น
ระบบปัจจุบันใช้ Hyperledger Besu `26.7.0`, QBFT **4 validators + 1 RPC**, Chain ID `20260720`
พร้อม Prometheus และ Grafana โค้ด backend เป็นผู้จัดการตัวตน สิทธิ์ผู้ใช้ รูปภาพ watermark และฐานข้อมูล
บน chain เก็บ opaque `bytes32`, เวลา และ address ผู้เขียน ไม่เก็บไฟล์หลักฐานหรือชื่อบุคคล

## โครงสร้างและแหล่งข้อมูลหลัก

| Path | หน้าที่ |
| --- | --- |
| `contracts/EvidenceRegistryV3.sol`, `contracts/interfaces/IEvidenceRegistryV3.sol` | contract และ API ปัจจุบัน |
| `blockchain_client/` | signer, nonce, ส่งธุรกรรม, อ่าน state/event, ตรวจธุรกรรมและสร้าง proof, benchmark |
| `script/` | Foundry deploy, grant/revoke roles, pause/unpause |
| `scripts/` | export artifact, สร้าง manifest, ตรวจ deployment |
| `test/`, `tests/` | Solidity และ Python tests |
| `network/besu/` | Compose, genesis, config nodes, monitoring และ operational scripts |
| `network/besu/deployments/20260720/EvidenceRegistryV3.json` | manifest สาธารณะของ deployment ปัจจุบัน |
| `lib/` | dependencies แบบ Git submodule; ไม่แก้เอกสาร upstream ให้เป็นเอกสารโครงการ |

รายละเอียด: [เครือข่าย](network/besu/README.md), [การปฏิบัติงาน](network/besu/docs/operations.md),
[monitoring](network/besu/docs/monitoring-dashboard.md), [backup/restore](network/besu/docs/backup-recovery.md),
[benchmark](network/besu/benchmarks/README.md), [proof](network/besu/proofs/README.md),
[การย้ายมา V3](MIGRATION.md), [ความปลอดภัย](SECURITY.md)

## เริ่มระบบที่มีอยู่แล้ว

รันจาก root ของ blockchain; shell scripts ใช้ Bash (Git Bash/WSL/Linux)
และ Python ต้องเป็น environment ของโมดูลนี้ ห้ามคัดลอก `.env.example` ทับ `.env` ที่มีอยู่

```bash
bash network/besu/scripts/start-network.sh
python network/besu/scripts/health-check.py --rpc-url http://127.0.0.1:8545 --expected-chain-id 20260720
```

RPC เปิดที่ `127.0.0.1:8545` โดยค่า port เปลี่ยนได้ผ่าน `RPC_HTTP_PORT`
Grafana ของ Compose หลักอยู่ที่ [localhost:3001](http://localhost:3001)
validator ปิด HTTP/WS RPC; RPC node เปิดเฉพาะ `ETH`, `NET`, `WEB3`
ขั้นตอนสร้าง chain ใหม่อยู่ในคู่มือ operations และไม่ใช่ขั้นตอนเริ่มระบบเดิม
Anvil Chain ID `31337` ใช้เฉพาะ environment ทดสอบแยกต่างหาก

## API และข้อมูล V3

```solidity
recordEvidence(bytes32 evidenceRef, bytes32 evidenceHash, bytes32 uploaderRef)
recordAccess(bytes32 evidenceRef, bytes32 officerRef, bytes32 accessSessionRef,
             AccessAction action, uint64 occurredAt)
getEvidence(bytes32 evidenceRef)
getAccessBySession(bytes32 accessSessionRef)
evidenceExists(bytes32 evidenceRef)
accessSessionExists(bytes32 accessSessionRef)
pause()
unpause()
```

`AccessAction.VIEW = 0`, `DOWNLOAD = 1` แต่ละ reference ต้องไม่เป็นศูนย์
`recordEvidence` ปฏิเสธ evidence ซ้ำ; `recordAccess` ต้องพบ evidence เดิมและ session ต้องไม่ซ้ำ
`occurredAt` เป็น Unix seconds จาก backend ต้องไม่เป็นศูนย์และอยู่ในช่วง uint64
contract ไม่ห้ามเวลาย้อนหลังหรืออนาคตเพิ่มเติม ส่วน `recordedAt` มาจาก `block.timestamp`
query ของรายการที่ไม่พบจะ revert; ใช้ `evidenceExists`/`accessSessionExists` ถ้าต้องการ boolean

`getEvidence` คืน `(evidenceHash, uploaderRef, recordedAt, writer, exists)`
และ `getAccessBySession` คืน `(evidenceRef, officerRef, action, occurredAt, recordedAt, writer)`
events คือ `EvidenceRecorded` และ `EvidenceAccessRecorded`; ดู indexed fields ใน interface
`Paused`/`Unpaused` เป็น events ของ OpenZeppelin

## สิทธิ์และการส่งธุรกรรม

| Role/account | หน้าที่ |
| --- | --- |
| Deployer | deploy เท่านั้น ไม่ได้รับ admin โดยอัตโนมัติ |
| `DEFAULT_ADMIN_ROLE` | grant/revoke roles |
| `WRITER_ROLE` | บันทึก evidence/access |
| `PAUSER_ROLE` | pause/unpause |

constructor รับ admin address ที่ไม่เป็นศูนย์และให้ admin ทั้ง `DEFAULT_ADMIN_ROLE` และ `PAUSER_ROLE`
Writer ต้องได้รับ role แยกต่างหาก การให้ Pauser คนใหม่ไม่ได้ถอน role ของ admin อัตโนมัติ
แยก node identity, Deployer, Admin, Pauser และ Writer ออกจากกัน

Python ใช้ `BlockchainClientSettings` และ inject `TransactionSigner` เช่น `LocalPrivateKeySigner`
ตั้ง `proof_of_authority=True` สำหรับ Besu QBFT, `chain_id=20260720`, contract address จาก manifest
และ artifact `out/EvidenceRegistryV3.sol/EvidenceRegistryV3.json`
`signer_private_key` ยังมีเพื่อ compatibility แต่ integration ใหม่ควร inject signer
client ไม่โหลด `.env` เอง; caller ต้องส่ง settings และ secret ที่จำเป็น

เรียก `client.record_evidence(evidence_ref, evidence_hash, uploader_ref)` และ
`client.record_access(evidence_ref, officer_ref, access_session_ref, AccessAction.DOWNLOAD, occurred_at)`
client ใช้ pending nonce ลงนาม raw transaction ตรวจ receipt/event และรอ confirmations ตาม settings
ผลมี tx hash, block number/timestamp, chain ID, contract address, confirmations และ decoded event
ข้อผิดพลาดเป็น typed exceptions ใน `blockchain_client/exceptions.py`

## Build และ tests แบบไม่แตะ chain จริง

Python รองรับ `>=3.11,<3.13`; package versions อยู่ใน `pyproject.toml`
Foundry CI pin `1.7.1`, Solidity `0.8.24`, EVM `london`
ติดตั้ง dependencies ใน virtual environment แยกและตรวจ submodules ก่อน build

```bash
git submodule update --init --recursive
python -m pip install -e '.[dev]'
forge fmt --check
forge build
forge test -vvv
forge test --gas-report
ruff check .
mypy blockchain_client
pytest -m 'not integration' -vv
```

CI มี 3 jobs: `solidity`, `python`, `besu-network`
job เครือข่ายใช้ ephemeral accounts/chain สำหรับ deploy, smoke และ failure tests
การลบ volumes ใน CI ใช้กับ environment ชั่วคราวเท่านั้น ไม่ใช่คำสั่งดูแล chain ปัจจุบัน

## Deploy และจัดการ roles

deploy เป็นงานสร้างธุรกรรมจริง ไม่ต้องทำซ้ำเพื่อแก้เอกสารหรือกู้ secret
สคริปต์ `network/besu/scripts/deploy-registry.sh` โหลด `network/besu/.env`
ต้องมี `CHAIN_ID`, `DEPLOYER_PRIVATE_KEY`, `ADMIN_PRIVATE_KEY`, `REGISTRY_ADMIN_ADDRESS`, `WRITER_ADDRESS`
สคริปต์ตรวจ chain ID, build, deploy V3, grant Writer, grant Pauser ถ้ากำหนดแยกจาก admin,
เขียน manifest และ `contract-address.env` แล้วตรวจ deployment
เรียกจาก root ของ blockchain เฉพาะเมื่ออนุมัติ deploy ใหม่แล้ว

งาน admin ใช้ `script/GrantWriterRole.s.sol`, `RevokeWriterRole.s.sol`,
`GrantPauserRole.s.sol`, `RevokePauserRole.s.sol` กับ `ADMIN_PRIVATE_KEY`
ส่วน `PauseRegistry.s.sol`/`UnpauseRegistry.s.sol` ใช้ `PAUSER_PRIVATE_KEY`
ทุกงานระบุ `CHAIN_ID`, `CONTRACT_ADDRESS`, `RPC_URL` และ role address ที่เกี่ยวข้อง
ไม่ใส่ private key ใน command line หรือเปิด shell tracing

ตรวจ deployment ที่มีอยู่แบบอ่านอย่างเดียว:

```bash
python scripts/verify_deployment.py --manifest network/besu/deployments/20260720/EvidenceRegistryV3.json
```

`scripts/generate_deployment_manifest.py` และ `scripts/export_artifact.py` ใช้สร้าง metadata/ABI
ดู options ด้วย `--help`; ไม่แก้ manifest ให้ชี้ address ใหม่โดยไม่ตรวจ chain

## Smoke และการวัดผล

`examples/manual_smoke_test.py`, `examples/manual_negative_smoke_test.py` และ
`network/besu/scripts/smoke-test.py` ส่งธุรกรรมจริง ต้องมี environment ทดสอบและ role ที่เหมาะสม
negative test ตรวจ duplicate evidence/session, unauthorized writer และ paused state
benchmark ส่งธุรกรรมจริงเช่นกัน; failure test หยุด validators จึงต้องวางแผนก่อนรัน
คำสั่ง proof แบบ `verify-*` อ่านธุรกรรมเดิม ส่วน `record-*` เขียน chain

## การแก้ปัญหาโดยรักษาข้อมูลเดิม

- ไม่มี artifact: รัน `forge build` และตรวจ path ที่ตั้งไว้
- Chain ID ไม่ตรง: ตรวจ RPC URL/manifest/environment; ไม่ reset network อัตโนมัติ
- ไม่พบ bytecode: ตรวจ chain, address และสถานะ sync ก่อนตัดสินใจเรื่อง deployment
- ไม่มีสิทธิ์: ตรวจ signer address และ role ของงานนั้น; อย่าเพิ่มสิทธิ์ทุกชนิดให้ Writer
- RPC ไม่ตอบ/ไม่มี peers: ตรวจ containers, port และ static peers ตามคู่มือ operations

## การจัดการ Secret และ Private Key สำหรับ Blockchain

ระบบแยกหน้าที่ของ key เพื่อจำกัดผลกระทบเมื่อ key ใด key หนึ่งรั่วไหล:

- **Validator Node Key** ใช้ระบุตัวตนและลงนามฉันทามติของ validator แต่ละตัว
- **RPC Node Key** ใช้เป็น P2P identity ของ RPC node และไม่ได้รับสิทธิ์ validator
- **Deployer Key** ใช้ส่งธุรกรรม deploy contract เท่านั้น
- **Contract Admin Key** ใช้ grant/revoke role ของ contract และไม่ควรอยู่ใน backend
- **Pauser Key** ใช้ pause/unpause contract ตามสิทธิ์ที่ได้รับ
- **Backend Writer Key** ใช้เฉพาะ `recordEvidence` และ `recordAccess` ใน runtime

Backend อ่านเพียง `BLOCKCHAIN_WRITER_PRIVATE_KEY` จาก `../backend/.env` และไม่ต้อง
ได้รับ Deployer, Contract Admin, Pauser หรือ Validator key ส่วนงาน deploy/administration
ใช้ environment ที่ `network/besu/.env` หรือ `.env` ของ repository นี้แยกต่างหาก

ค่าที่เปิดเผยได้ ได้แก่ Chain ID, contract address, deployment block, transaction hash,
writer/validator address, ABI, genesis, Evidence Ref, officerRef และ accessSessionRef
ส่วน private key ทุกชนิดห้ามใส่ใน Git, README, `.env.example`, frontend, API response,
Blockchain Explorer, log, chat หรือ email แบบ plaintext

### ไฟล์ที่ต้องสำรอง

| รายการ | Path | ความสำคัญ | Secret | Git |
|---|---|---|---|---|
| Validator 1 identity | `network/besu/keys/validator-1/key` | สูงสุด ใช้กู้ identity เดิม | ใช่ | ignored |
| Validator 2 identity | `network/besu/keys/validator-2/key` | สูงสุด ใช้กู้ identity เดิม | ใช่ | ignored |
| Validator 3 identity | `network/besu/keys/validator-3/key` | สูงสุด ใช้กู้ identity เดิม | ใช่ | ignored |
| Validator 4 identity | `network/besu/keys/validator-4/key` | สูงสุด ใช้กู้ identity เดิม | ใช่ | ignored |
| RPC node identity | `network/besu/keys/rpc-node/key` | สูง ใช้กู้ P2P identity เดิม | ใช่ | ignored |
| Deployer/Admin/Pauser/Writer สำหรับงานดูแลระบบ | `.env`, `network/besu/.env` | สูงสุด ใช้ deploy และจัดการ role | ใช่ | ignored |
| Backend Writer สำหรับ runtime | `../backend/.env` | สูงสุด ใช้เขียนรายการจาก backend | ใช่ | ignored |
| Generated validator key copies | `network/besu/build/keys/*/key` | สำเนาที่สร้างระหว่าง generate network | ใช่ | ignored |

ให้สำรอง secret เป็น archive ที่เข้ารหัสอย่างน้อย 2 ชุด เก็บคนละตำแหน่งบนสื่อหรือ
secure storage ที่ควบคุมสิทธิ์ เช่น encrypted external drive ห้ามส่ง password และ archive
ผ่านช่องทางเดียวกัน และไม่ควรสำรอง generated key copy ซ้ำหากมี canonical key ใต้
`network/besu/keys/` ครบแล้ว

ไฟล์ recovery ที่ไม่ใช่ secret แต่ต้องรักษาไว้ ได้แก่:

- `network/besu/genesis/genesis.json` และ `network/besu/build/static-nodes.json` เป็น
  generated recovery config ที่ถูก Git ignore จึงต้องรวมใน backup ของ network
- `network/besu/genesis/qbftConfigFile.json`, `network/besu/nodes/*/config.toml`,
  `network/besu/docker-compose.yml` และ `network/besu/monitoring/` อยู่ใน Git
- `network/besu/deployments/20260720/EvidenceRegistryV3.json`,
  `tests/fixtures/EvidenceRegistryV3.json` และ `contracts/EvidenceRegistryV3.sol` อยู่ใน Git

chain state อยู่ใน Docker volumes `evidence-besu-qbft_validator-1-data` ถึง
`evidence-besu-qbft_validator-4-data` และ `evidence-besu-qbft_rpc-node-data` ซึ่ง Git
ไม่สามารถสำรองแทนได้ การสำรอง production ในอนาคตต้องมีแผน snapshot/restore volumes
แยกจาก secret backup และต้องทดสอบการกู้คืนจริง

หาก node key สูญหาย จะไม่สามารถสร้าง identity เดิมจาก public address ได้ หาก writer
key รั่วให้ grant writer ใหม่ก่อน revoke ตัวเก่า และหาก admin/pauser key รั่วให้ย้าย role
ไป account ใหม่ด้วยขั้นตอนที่ตรวจสอบได้ ห้าม generate key ทดแทนหรือ redeploy อัตโนมัติ
โดยยังไม่ประเมินผลกระทบ สำหรับ production จริงสามารถพิจารณา Vault/HSM เป็นขั้นถัดไปได้


ขั้นตอนเข้ารหัส ตรวจ checksum และ restore อยู่ใน [backup-recovery.md](network/besu/docs/backup-recovery.md)

ดู [รายงาน cleanup และ tests](network/besu/docs/maintenance-audit.md) สำหรับหลักฐาน dependency รายไฟล์และข้อจำกัดผลตรวจรอบนี้
