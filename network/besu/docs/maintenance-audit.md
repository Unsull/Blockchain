# ผลตรวจไฟล์และเอกสาร Blockchain — 9 กันยายน 2026

ตรวจแบบ read-only ก่อนแก้ไขจาก blockchain commit `6dfd49a` และ parent `f186bff`
อ่าน tracked files 136 รายการ, ignored files 372 รายการ และ references จาก parent integration
ค้น path/filename/Python modules ประกอบการตรวจ CI, Foundry/pytest discovery, imports, Compose mounts และ CLI entry points
การไม่พบชื่อไฟล์จาก search เพียงอย่างเดียวไม่ใช่หลักฐานว่าลบได้ โดยเฉพาะ CLI, tests, เอกสารและข้อมูล runtime

## รายการตัดสินใจ

| กลุ่ม | สถานะ | หลักฐาน/เหตุผล |
| --- | --- | --- |
| `examples/legacy_api_example.py` | SAFE_TO_DELETE — ลบแล้ว | FastAPI marker เก่า ไม่มี code/parent consumer; อ้างเฉพาะ README เดิมบรรทัด 465 และ MIGRATION เดิมบรรทัด 28 ซึ่งปรับแล้ว; package excludes examples |
| `network/genesis.example.json` | SAFE_TO_DELETE — ลบแล้ว | generic chain 31337 ไม่มี QBFT และไม่มี references; generator ใช้ `network/besu/genesis/qbftConfigFile.json`; Compose mount generated `genesis/genesis.json` |
| `network/static-nodes.example.json` | SAFE_TO_DELETE — ลบแล้ว | placeholder topology เก่า ไม่มี references; renderer เขียน `network/besu/build/static-nodes.json` ซึ่ง Compose mount จริง |
| `network/besu/genesis/genesis.json.example` | UNCERTAIN — เก็บ | ไม่พบ consumer อัตโนมัติ แต่เป็นตัวอย่าง config ใน Besu tree; ไม่จำเป็นต้องลบเพื่อล้าง active runtime |
| `contracts/`, `script/`, `test/`, `lib/` | KEEP | Foundry config/remappings, imports, deployment และ test discovery |
| `blockchain_client/`, `tests/`, `scripts/`, manual smoke examples | KEEP | package discovery/imports, pytest, backend integration และ CLI ที่เรียกด้วยมือ |
| `network/besu/scripts/` | KEEP | CI/run/deploy/test/monitoring และ CLI operations แม้บางไฟล์ไม่มี caller อัตโนมัติ |
| Compose, node configs, monitoring, V3 manifest/ABI, scenarios | KEEP | mounts, provisioning, deployment verifier, tests และ benchmark loader |
| `nodes/*/data/.gitkeep` | KEEP | placeholders; reset script ยังอ้าง `nodes/*/data`; named volumes เป็นคนละส่วน |
| ignored `.env`, canonical keys, `build/`, `broadcast/`, `out/`, caches | KEEP | secrets/runtime/generated artifacts และประวัติ deployment; ไม่ลบเป็นส่วนหนึ่งของ source cleanup |
| upstream `lib/**/*.md`, generated reports/proofs/results ถ้ามี | KEEP | เอกสาร dependency และหลักฐานตามเวลาเดิม ไม่เขียนทับเป็นผล network ปัจจุบัน |

## Markdown ที่ปรับ

- `MIGRATION.md`
- `README.md`
- `SECURITY.md`
- `network/README.md`
- `network/besu/README.md`
- `network/besu/benchmarks/README.md`
- `network/besu/docs/architecture.md`
- `network/besu/docs/backup-recovery.md`
- `network/besu/docs/failure-testing.md`
- `network/besu/docs/monitoring-dashboard.md`
- `network/besu/docs/operations.md`
- `network/besu/docs/security.md`
- `network/besu/monitoring/discovered-metrics.md`
- `network/besu/proofs/README.md`
- `network/security-checklist.md`

ปรับเอกสารโครงการเดิมครบ 15 ไฟล์ และเพิ่มรายงานนี้อีก 1 ไฟล์
แก้ V3 API/action/timestamps, Geth/legacy guidance, port Grafana 3001 และ semantics ของ monitoring override
แยก run เดิม, generate ใหม่, deploy และ tests ที่ส่งธุรกรรม พร้อม backup/checksum/restore ภาษาไทย
metric snapshot เก็บวันที่และค่าตัวอย่างเดิม โดยแปลคำอธิบายและระบุว่าไม่ใช่ live state

## ผลตรวจ

- Python: `pytest -m "not integration"` ผ่าน 181 tests
- Solidity: Foundry 1.7.1, fmt/build/gas report ผ่าน; tests ผ่าน 19 tests รวม fuzz/invariant
- Ruff ผ่าน; Mypy ผ่าน 21 source files
- Compose หลักและ monitoring override validate ผ่าน; generated keys/public metadata/genesis/static peers/IPAM mapping ผ่าน
- Backup AES-256-GCM: inventory 10 + public metadata 5 ไฟล์; round-trip byte comparison/SHA-256 ผ่าน; wrong key/tamper ถูกปฏิเสธ
- Live health/deployment verification ทำไม่สำเร็จ: RPC localhost:8545 ปฏิเสธ connection; ไม่อ้างว่า chain/roles/live dashboard ผ่านในรอบนี้
- ไม่รัน live smoke/benchmark/failure tests; ไม่เริ่ม/reset network หรือเปลี่ยน volumes/role/contract

ตรวจเพิ่มเติม: Python AST, JSON/YAML, Bash syntax, Markdown local links/fences, current-secret scan ในเอกสาร/diff และ `git diff --check` ผ่าน

ทดสอบ restore ลงโฟลเดอร์ชั่วคราวที่จำกัดสิทธิ์แล้ว เทียบครบ 15 ไฟล์กับต้นฉบับและลบสำเนาทดสอบเรียบร้อย

## หลักฐาน dependency รายไฟล์ (ก่อนแก้ไข)

references ในตารางอ้าง line numbers ของ commit ตั้งต้น; เป็น textual references ต้องอ่านร่วมกับเหตุผลข้างต้น
เครื่องหมาย — หมายถึงไม่พบ textual reference หรือใช้ implicit/manual discovery ไม่ได้แปลว่าไม่มีการใช้งาน

| Path | สถานะ | References ตัวอย่าง |
| --- | --- | --- |
| `.env.anvil.example` | KEEP | `README.md:232` |
| `.env.example` | KEEP | `.github/workflows/ci.yml:54`, `.github/workflows/ci.yml:81`, `.github/workflows/ci.yml:108`, `.github/workflows/ci.yml:129`, `.github/workflows/ci.yml:135` |
| `.gitattributes` | KEEP | — |
| `.github/workflows/ci.yml` | KEEP | — |
| `.gitignore` | KEEP | `../backend/tests/test_migration_compatibility.py:77` |
| `.gitmodules` | KEEP | — |
| `MIGRATION.md` | KEEP | `README.md:466` |
| `README.md` | KEEP | `.gitignore:23`, `network/README.md:9`, `../README.md:169`, `../README.md:177`, `../README.md:179` |
| `SECURITY.md` | KEEP | — |
| `blockchain_client/__init__.py` | KEEP | — |
| `blockchain_client/artifacts.py` | KEEP | `blockchain_client/client.py:11`, `tests/test_artifacts.py:5` |
| `blockchain_client/benchmark_analysis.py` | KEEP | `network/besu/scripts/analyze-benchmark-results.py:7`, `tests/test_benchmark_analysis.py:9` |
| `blockchain_client/benchmark_export.py` | KEEP | `network/besu/scripts/benchmark-transactions.py:16`, `tests/test_benchmark_export.py:8` |
| `blockchain_client/benchmark_models.py` | KEEP | `blockchain_client/benchmark_export.py:10`, `blockchain_client/benchmark_runner.py:10`, `blockchain_client/benchmark_scenarios.py:8`, `blockchain_client/benchmark_stats.py:5`, `tests/test_benchmark_cli.py:11` |
| `blockchain_client/benchmark_observer.py` | KEEP | `network/besu/scripts/benchmark-transactions.py:17`, `tests/test_benchmark_observer.py:11` |
| `blockchain_client/benchmark_runner.py` | KEEP | `network/besu/scripts/benchmark-transactions.py:22`, `tests/test_benchmark_runner.py:8` |
| `blockchain_client/benchmark_scenarios.py` | KEEP | `network/besu/scripts/benchmark-transactions.py:23`, `tests/test_benchmark_cli.py:12`, `tests/test_benchmark_scenarios.py:8` |
| `blockchain_client/benchmark_stats.py` | KEEP | `network/besu/scripts/benchmark-transactions.py:27`, `tests/test_benchmark_export.py:14`, `tests/test_benchmark_stats.py:12` |
| `blockchain_client/client.py` | KEEP | `blockchain_client/__init__.py:3`, `blockchain_client/proof_builder.py:10`, `blockchain_client/transaction_verifier.py:9`, `network/besu/scripts/benchmark-transactions.py:28`, `tests/test_client_events.py:9` |
| `blockchain_client/config.py` | KEEP | `blockchain_client/__init__.py:4`, `blockchain_client/client.py:12`, `network/besu/scripts/benchmark-transactions.py:29`, `tests/test_config.py:5`, `tests/test_confirmations.py:7` |
| `blockchain_client/exceptions.py` | KEEP | `README.md:345`, `blockchain_client/artifacts.py:7`, `blockchain_client/client.py:13`, `blockchain_client/config.py:8`, `blockchain_client/nonce.py:6` |
| `blockchain_client/models.py` | KEEP | `blockchain_client/__init__.py:5`, `blockchain_client/benchmark_runner.py:15`, `blockchain_client/client.py:28`, `blockchain_client/proof_builder.py:11`, `blockchain_client/proof_models.py:11` |
| `blockchain_client/nonce.py` | KEEP | `blockchain_client/client.py:35`, `tests/test_nonce_manager.py:6` |
| `blockchain_client/proof_builder.py` | KEEP | `blockchain_client/__init__.py:14`, `tests/test_proof_builder.py:14` |
| `blockchain_client/proof_models.py` | KEEP | `blockchain_client/__init__.py:15`, `blockchain_client/proof_builder.py:12`, `blockchain_client/proof_renderer.py:10`, `network/besu/scripts/transaction-proof.py:28`, `tests/proof_fixtures.py:5` |
| `blockchain_client/proof_renderer.py` | KEEP | `network/besu/scripts/transaction-proof.py:29`, `tests/test_proof_renderer.py:6` |
| `blockchain_client/reference_derivation.py` | KEEP | `blockchain_client/__init__.py:16` |
| `blockchain_client/references.py` | KEEP | `blockchain_client/client.py:36`, `blockchain_client/proof_builder.py:20`, `blockchain_client/proof_models.py:12`, `blockchain_client/reference_derivation.py:7`, `blockchain_client/transaction_verifier.py:12` |
| `blockchain_client/signer.py` | KEEP | `blockchain_client/__init__.py:21`, `blockchain_client/client.py:37`, `tests/test_signer.py:7` |
| `blockchain_client/transaction_verifier.py` | KEEP | `blockchain_client/proof_builder.py:21`, `network/besu/scripts/smoke-test.py:19`, `tests/test_transaction_verifier.py:15` |
| `contracts/EvidenceRegistryV3.sol` | KEEP | `README.md:73`, `README.md:193`, `README.md:280`, `README.md:309`, `README.md:362` |
| `contracts/interfaces/IEvidenceRegistryV3.sol` | KEEP | `contracts/EvidenceRegistryV3.sol:6`, `test/EvidenceRegistryFuzz.t.sol:6`, `test/EvidenceRegistryInvariant.t.sol:6`, `test/EvidenceRegistryV3.t.sol:8` |
| `deployments/example/EvidenceRegistryV3.manifest.json` | KEEP | `README.md:309`, `README.md:310` |
| `examples/legacy_api_example.py` | SAFE_TO_DELETE | `MIGRATION.md:28`, `README.md:465` |
| `examples/manual_negative_smoke_test.py` | KEEP | `README.md:298` |
| `examples/manual_smoke_test.py` | KEEP | `README.md:297` |
| `foundry.lock` | KEEP | `README.md:129` |
| `foundry.toml` | KEEP | — |
| `lib/forge-std` | KEEP | `.gitmodules:4`, `.gitmodules:5`, `.gitmodules:6`, `foundry.lock:2`, `foundry.toml:12` |
| `lib/openzeppelin-contracts` | KEEP | `.gitmodules:1`, `.gitmodules:2`, `.gitmodules:3`, `foundry.lock:8`, `foundry.toml:11` |
| `network/README.md` | KEEP | `.gitignore:23` |
| `network/besu/.env.anvil.example` | KEEP | `README.md:232` |
| `network/besu/.env.example` | KEEP | `.github/workflows/ci.yml:54`, `.github/workflows/ci.yml:81`, `.github/workflows/ci.yml:108`, `.github/workflows/ci.yml:129`, `.github/workflows/ci.yml:135` |
| `network/besu/README.md` | KEEP | `.gitignore:23`, `network/README.md:9` |
| `network/besu/benchmarks/README.md` | KEEP | `.gitignore:23`, `network/README.md:9` |
| `network/besu/benchmarks/scenarios.json` | KEEP | `network/besu/benchmarks/README.md:108`, `network/besu/benchmarks/README.md:303`, `network/besu/benchmarks/README.md:320`, `network/besu/benchmarks/README.md:352`, `network/besu/benchmarks/README.md:611` |
| `network/besu/deployments/20260720/EvidenceRegistryV3.json` | KEEP | `.gitignore:41`, `README.md:193`, `README.md:279`, `README.md:280`, `README.md:309` |
| `network/besu/docker-compose.monitoring.yml` | KEEP | `network/besu/docs/monitoring-dashboard.md:28`, `network/besu/docs/monitoring-dashboard.md:162` |
| `network/besu/docker-compose.yml` | KEEP | `README.md:278`, `network/besu/docs/backup-recovery.md:9`, `network/besu/docs/monitoring-dashboard.md:27`, `network/besu/docs/monitoring-dashboard.md:161` |
| `network/besu/docs/architecture.md` | KEEP | — |
| `network/besu/docs/backup-recovery.md` | KEEP | — |
| `network/besu/docs/failure-testing.md` | KEEP | — |
| `network/besu/docs/monitoring-dashboard.md` | KEEP | — |
| `network/besu/docs/operations.md` | KEEP | `network/besu/README.md:56` |
| `network/besu/docs/security.md` | KEEP | — |
| `network/besu/genesis/genesis.json.example` | UNCERTAIN | — |
| `network/besu/genesis/qbftConfigFile.json` | KEEP | `README.md:277`, `network/besu/scripts/generate-network.sh:31`, `network/besu/scripts/generate-network.sh:69` |
| `network/besu/monitoring/alert-rules.yml` | KEEP | `network/besu/docker-compose.yml:166`, `network/besu/monitoring/prometheus.yml:6` |
| `network/besu/monitoring/discovered-metrics.md` | KEEP | — |
| `network/besu/monitoring/grafana/provisioning/dashboards/besu-qbft-overview.json` | KEEP | `tests/test_grafana_dashboard.py:9` |
| `network/besu/monitoring/grafana/provisioning/dashboards/dashboards.yml` | KEEP | — |
| `network/besu/monitoring/grafana/provisioning/datasources/prometheus.yml` | KEEP | `network/besu/docker-compose.yml:162`, `network/besu/docker-compose.yml:165` |
| `network/besu/monitoring/prometheus.yml` | KEEP | `network/besu/docker-compose.yml:162`, `network/besu/docker-compose.yml:165` |
| `network/besu/nodes/rpc-node/config.toml` | KEEP | `README.md:277`, `network/besu/docker-compose.yml:50`, `network/besu/docker-compose.yml:53`, `network/besu/docker-compose.yml:71`, `network/besu/docker-compose.yml:74` |
| `network/besu/nodes/rpc-node/data/.gitkeep` | KEEP | `.gitignore:28`, `network/besu/scripts/reset-network.sh:17` |
| `network/besu/nodes/validator-1/config.toml` | KEEP | `README.md:277`, `network/besu/docker-compose.yml:50`, `network/besu/docker-compose.yml:53`, `network/besu/docker-compose.yml:71`, `network/besu/docker-compose.yml:74` |
| `network/besu/nodes/validator-1/data/.gitkeep` | KEEP | `.gitignore:28`, `network/besu/scripts/reset-network.sh:17` |
| `network/besu/nodes/validator-2/config.toml` | KEEP | `README.md:277`, `network/besu/docker-compose.yml:50`, `network/besu/docker-compose.yml:53`, `network/besu/docker-compose.yml:71`, `network/besu/docker-compose.yml:74` |
| `network/besu/nodes/validator-2/data/.gitkeep` | KEEP | `.gitignore:28`, `network/besu/scripts/reset-network.sh:17` |
| `network/besu/nodes/validator-3/config.toml` | KEEP | `README.md:277`, `network/besu/docker-compose.yml:50`, `network/besu/docker-compose.yml:53`, `network/besu/docker-compose.yml:71`, `network/besu/docker-compose.yml:74` |
| `network/besu/nodes/validator-3/data/.gitkeep` | KEEP | `.gitignore:28`, `network/besu/scripts/reset-network.sh:17` |
| `network/besu/nodes/validator-4/config.toml` | KEEP | `README.md:277`, `network/besu/docker-compose.yml:50`, `network/besu/docker-compose.yml:53`, `network/besu/docker-compose.yml:71`, `network/besu/docker-compose.yml:74` |
| `network/besu/nodes/validator-4/data/.gitkeep` | KEEP | `.gitignore:28`, `network/besu/scripts/reset-network.sh:17` |
| `network/besu/proofs/README.md` | KEEP | `.gitignore:23`, `network/README.md:9` |
| `network/besu/scripts/analyze-benchmark-results.py` | KEEP | `blockchain_client/benchmark_analysis.py:595`, `network/besu/benchmarks/README.md:595` |
| `network/besu/scripts/benchmark-transactions.py` | KEEP | `network/besu/benchmarks/README.md:314`, `network/besu/benchmarks/README.md:334`, `network/besu/benchmarks/README.md:343`, `network/besu/benchmarks/README.md:351`, `network/besu/benchmarks/README.md:358` |
| `network/besu/scripts/deploy-registry.sh` | KEEP | `.github/workflows/ci.yml:62`, `.github/workflows/ci.yml:144`, `network/besu/README.md:53`, `network/besu/docs/operations.md:61` |
| `network/besu/scripts/discover-prometheus-metrics.py` | KEEP | `tests/test_discover_prometheus_metrics.py:9` |
| `network/besu/scripts/failure-test.py` | KEEP | `.github/workflows/ci.yml:161`, `network/besu/README.md:52`, `network/besu/docs/failure-testing.md:12` |
| `network/besu/scripts/fund-genesis.py` | KEEP | `.github/workflows/ci.yml:116`, `network/besu/README.md:15`, `network/besu/docs/operations.md:26` |
| `network/besu/scripts/generate-network.sh` | KEEP | `.github/workflows/ci.yml:58`, `.github/workflows/ci.yml:110`, `README.md:63`, `network/README.md:26`, `network/besu/README.md:14` |
| `network/besu/scripts/health-check.py` | KEEP | `network/besu/README.md:50`, `network/besu/docs/operations.md:52`, `network/besu/scripts/start-network.sh:25` |
| `network/besu/scripts/render-static-nodes.py` | KEEP | `network/besu/docs/operations.md:18`, `network/besu/scripts/generate-network.sh:105` |
| `network/besu/scripts/reset-network.sh` | KEEP | `.github/workflows/ci.yml:61` |
| `network/besu/scripts/smoke-test.py` | KEEP | `.github/workflows/ci.yml:155`, `network/besu/README.md:51` |
| `network/besu/scripts/start-network.sh` | KEEP | `.github/workflows/ci.yml:59`, `.github/workflows/ci.yml:131`, `README.md:64`, `network/README.md:27`, `network/besu/README.md:17` |
| `network/besu/scripts/stop-network.sh` | KEEP | `.github/workflows/ci.yml:60`, `network/besu/docs/operations.md:38` |
| `network/besu/scripts/transaction-proof.py` | KEEP | `tests/test_transaction_proof_cli.py:15` |
| `network/besu/scripts/validate-generated-network.py` | KEEP | `.github/workflows/ci.yml:123`, `network/besu/docs/operations.md:19`, `network/besu/scripts/generate-network.sh:109` |
| `network/besu/scripts/validate-monitoring-dashboard.py` | KEEP | — |
| `network/besu/scripts/wait-for-rpc.py` | KEEP | `network/besu/scripts/deploy-registry.sh:21`, `network/besu/scripts/start-network.sh:22` |
| `network/genesis.example.json` | SAFE_TO_DELETE | — |
| `network/security-checklist.md` | KEEP | — |
| `network/static-nodes.example.json` | SAFE_TO_DELETE | — |
| `pyproject.toml` | KEEP | — |
| `script/DeployEvidenceRegistryV3.s.sol` | KEEP | `README.md:150`, `network/besu/scripts/deploy-registry.sh:30`, `network/besu/scripts/deploy-registry.sh:35` |
| `script/GrantPauserRole.s.sol` | KEEP | `README.md:167`, `network/besu/scripts/deploy-registry.sh:68` |
| `script/GrantWriterRole.s.sol` | KEEP | `README.md:162`, `README.md:395`, `README.md:401`, `network/besu/scripts/deploy-registry.sh:53`, `network/besu/scripts/deploy-registry.sh:54` |
| `script/PauseRegistry.s.sol` | KEEP | `README.md:174`, `examples/manual_negative_smoke_test.py:143` |
| `script/RevokePauserRole.s.sol` | KEEP | `README.md:167` |
| `script/RevokeWriterRole.s.sol` | KEEP | `README.md:163` |
| `script/UnpauseRegistry.s.sol` | KEEP | `README.md:175`, `examples/manual_negative_smoke_test.py:169` |
| `scripts/export_artifact.py` | KEEP | `README.md:311` |
| `scripts/generate_deployment_manifest.py` | KEEP | `README.md:309`, `network/besu/scripts/deploy-registry.sh:71` |
| `scripts/verify_deployment.py` | KEEP | `README.md:310`, `network/besu/scripts/deploy-registry.sh:86` |
| `test/EvidenceRegistryAccessControl.t.sol` | KEEP | — |
| `test/EvidenceRegistryFuzz.t.sol` | KEEP | — |
| `test/EvidenceRegistryInvariant.t.sol` | KEEP | — |
| `test/EvidenceRegistryV3.t.sol` | KEEP | — |
| `tests/fixtures/EvidenceRegistryV3.json` | KEEP | `.gitignore:41`, `README.md:193`, `README.md:279`, `README.md:280`, `README.md:309` |
| `tests/proof_fixtures.py` | KEEP | `tests/test_proof_builder.py:15`, `tests/test_proof_models.py:8`, `tests/test_proof_renderer.py:12`, `tests/test_transaction_proof_cli.py:11` |
| `tests/test_artifacts.py` | KEEP | — |
| `tests/test_benchmark_analysis.py` | KEEP | — |
| `tests/test_benchmark_cli.py` | KEEP | — |
| `tests/test_benchmark_export.py` | KEEP | — |
| `tests/test_benchmark_models.py` | KEEP | — |
| `tests/test_benchmark_observer.py` | KEEP | — |
| `tests/test_benchmark_runner.py` | KEEP | — |
| `tests/test_benchmark_scenarios.py` | KEEP | — |
| `tests/test_benchmark_stats.py` | KEEP | — |
| `tests/test_client.py` | KEEP | — |
| `tests/test_client_events.py` | KEEP | — |
| `tests/test_client_v3.py` | KEEP | — |
| `tests/test_config.py` | KEEP | — |
| `tests/test_confirmations.py` | KEEP | — |
| `tests/test_discover_prometheus_metrics.py` | KEEP | — |
| `tests/test_grafana_dashboard.py` | KEEP | — |
| `tests/test_nonce_manager.py` | KEEP | — |
| `tests/test_proof_builder.py` | KEEP | — |
| `tests/test_proof_models.py` | KEEP | — |
| `tests/test_proof_renderer.py` | KEEP | — |
| `tests/test_reference_derivation.py` | KEEP | — |
| `tests/test_references.py` | KEEP | — |
| `tests/test_signer.py` | KEEP | — |
| `tests/test_transaction_proof_cli.py` | KEEP | — |
| `tests/test_transaction_verifier.py` | KEEP | — |
