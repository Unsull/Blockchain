# Runtime artifact ของ EvidenceRegistryV3

`EvidenceRegistryV3.json` เป็น artifact ที่ commit ไว้สำหรับ backend และเครื่องมือ Python
เพื่อโหลด ABI ได้หลัง clone repository โดยไม่ต้องรัน `forge build` ก่อน ไฟล์นี้เป็นข้อมูลสาธารณะ
และไม่มี private key หรือ secret

เมื่อ contract หรือ compiler configuration เปลี่ยน ให้ build และ export ใหม่จาก root ของ blockchain:

```bash
forge build
python scripts/export_artifact.py --output artifacts/EvidenceRegistryV3.json
```

CI จะ export artifact จากผล build อีกครั้งและเปรียบเทียบกับไฟล์นี้แบบ byte-for-byte
หากไม่ตรงกัน job `solidity` จะไม่ผ่าน จึงต้อง commit contract และ runtime artifact พร้อมกัน
