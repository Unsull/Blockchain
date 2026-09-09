# การปฏิบัติงาน Besu

ทุกคำสั่งด้านล่างเริ่มจาก root ของ blockchain และ shell scripts ใช้ Bash
ระบบที่มีอยู่แล้วใช้ genesis/keys/volumes เดิม, Chain ID `20260720` และ EvidenceRegistryV3

## อ่านสถานะโดยไม่เขียน chain

```bash
docker compose --project-directory network/besu config --quiet
docker compose --project-directory network/besu ps
python network/besu/scripts/health-check.py --rpc-url http://127.0.0.1:8545 --expected-chain-id 20260720
python network/besu/scripts/validate-generated-network.py --root network/besu --expected-validators 4
python scripts/verify_deployment.py --manifest network/besu/deployments/20260720/EvidenceRegistryV3.json
```

ใช้ `config --quiet` เมื่อตรวจ syntax เพื่อไม่พิมพ์ credentials ที่ Compose resolve จาก `.env`
ดู logs เฉพาะเครื่องที่ควบคุมสิทธิ์และตรวจข้อมูลก่อนนำไปแชร์

## เริ่มและหยุดโดยรักษา volumes

```bash
bash network/besu/scripts/start-network.sh
bash network/besu/scripts/stop-network.sh
```

start โหลด `.env`, ตรวจว่ามี genesis, เรียก Compose, รอ RPC และ health check
หยุดใช้ `stop-network.sh` หรือ Compose `down` โดยไม่ใส่ `-v`
ดู Grafana หลักที่ `http://127.0.0.1:3001`

## สร้าง chain ใหม่เท่านั้น

ใช้ส่วนนี้เฉพาะ directory/environment ใหม่ที่ไม่มี chain state และได้รับอนุมัติแล้ว
เตรียม `.env` จาก example โดยสร้าง keys ของแต่ละบทบาทแยกกันผ่านช่องทางที่ปลอดภัย
`generate-network.sh` สร้าง node identities ใหม่; option `--force` ลบ generated keys/genesis เดิม
จึงไม่ใช้ option นี้เป็น quick start หรือวิธีแก้ config ของ chain ที่มีอยู่

```bash
bash network/besu/scripts/generate-network.sh
python network/besu/scripts/fund-genesis.py --genesis network/besu/genesis/genesis.json --address 0xPUBLIC_DEPLOYER_ADDRESS --address 0xPUBLIC_ADMIN_ADDRESS --address 0xPUBLIC_WRITER_ADDRESS
bash network/besu/scripts/start-network.sh
```

แทน placeholder ด้วย public addresses จริงก่อนรัน; fund-genesis รับเฉพาะ address
เพิ่มบัญชี Pauser/บัญชีทดสอบตามที่จำเป็นก่อนเริ่ม chain ครั้งแรก
ห้ามแก้ genesis alloc หลัง initialize chain data แล้ว

## Deploy V3 ใหม่เมื่อจำเป็นเท่านั้น

เตรียม environment ดู [README หลัก](../../../README.md)
รัน `bash network/besu/scripts/deploy-registry.sh` จาก root
สคริปต์ clean/build, ตรวจ chain ID, deploy, grant Writer/Pauser ตาม config และ verify manifest
ผลอยู่ `network/besu/deployments/<chain-id>/EvidenceRegistryV3.json` และ `contract-address.env`
ห้ามรันซ้ำเพื่อแก้เอกสารหรือ restore secret; ใช้ manifest/contract เดิม
role scripts ใน `script/` เป็นธุรกรรมจริงและใช้ administrative secrets แยกจาก backend

## ซ่อม static peers เมื่อเปลี่ยน IP

หลังตรวจ IPAM และ public keys เดิมแล้ว ใน Bash:

```bash
set -a
source network/besu/.env
set +a
python network/besu/scripts/render-static-nodes.py --keys-dir network/besu/keys --output network/besu/build/static-nodes.json
python network/besu/scripts/validate-generated-network.py --root network/besu --expected-validators 4
```

คำสั่งนี้เขียน static config; ไม่สร้าง identity หรือ genesis ใหม่ ต้องวางแผน restart ตามผลกระทบ

## Tests และข้อผิดพลาด

ทดสอบ offline ตาม README หลักก่อน smoke/benchmark ที่ส่งธุรกรรมจริง
failure test หยุด validators; ทำเฉพาะ environment ทดสอบตาม [คู่มือ](failure-testing.md)
RPC ไม่ตอบ: ตรวจ container/port; ไม่มี peers: ตรวจ IPAM/static peers/public key
block ไม่เพิ่ม: ตรวจอย่างน้อย 3 validators, connectivity และ logs
chain ID/address/genesis ไม่ตรง: ตรวจ environment และกู้ config เดิมจาก backup ไม่ reset data อัตโนมัติ
key ไม่ตรง: กู้ identity เดิม; ไม่มี bytecode: ตรวจ chain/address/sync ก่อนพิจารณา deploy
insufficient funds และ unauthorized role ต้องวางแผน funding/role transaction แยกจากการตรวจสถานะ
