# การทดสอบเครือข่ายขัดข้อง

`scripts/failure-test.py` เรียก Docker เพื่อหยุด/เริ่ม validators จึงกระทบ availability
ใช้เฉพาะ environment ทดสอบหรือช่วงเวลาที่อนุมัติแล้ว ไม่ใช่ read-only health check

สคริปต์ทดสอบหยุด validator-4 แล้ว block ยังเพิ่ม, หยุด validator-3 และ validator-4 แล้ว block หยุด,
จากนั้นเริ่ม validators กลับและตรวจ block production ฟื้นตัว

จาก root ของ blockchain:

```bash
python network/besu/scripts/failure-test.py --rpc-url http://127.0.0.1:8545
```

ผลอยู่ `network/besu/logs/failure-test-results.json` ซึ่ง Git ignore
ตรวจ options ระยะเวลารอด้วย `--help`; เก็บ timestamp/config และผลจริงก่อนสรุปว่าผ่าน

กรณีเพิ่มเติม เช่น RPC หยุดแล้ว sync กลับ, การกู้ data ของ node, revoke Writer หรือ pause contract
ต้องมีแผนแยก เพราะบางกรณีลบ data หรือเปลี่ยน role/state จริง
ทดสอบ volume recovery บนสำเนาเครือข่ายที่แยกไว้ ไม่ลบ volumes ของระบบปัจจุบันระหว่าง audit
ดู [backup-recovery](backup-recovery.md)
