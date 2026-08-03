# Evidence Blockchain Module

This repository contains the private EVM blockchain module for a digital
evidence platform. It records and verifies opaque evidence and access
references only. Watermarking, image storage, authentication, officer identity
mapping, and application database logic are intentionally out of scope.

## Scope

The module provides:

- `EvidenceRegistry` smart contract for immutable evidence and access records.
- Foundry deployment and role-management scripts.
- Python `blockchain_client` package for signed raw transactions, event decoding,
  state queries, and historical transaction verification.
- Private network guidance and a Besu QBFT Docker Compose stack for integration
  and staging.

## Out Of Scope

This module does not implement frontend UI, FastAPI business endpoints,
watermark embedding/extraction, PostgreSQL persistence, officer databases,
proxy keys, AES payloads, authentication, or image storage.

## Architecture

Backend systems derive opaque `bytes32` references and send them to this module:

- `evidence_ref`: backend-owned evidence identifier hash.
- `static_hash`: static evidence/watermark hash.
- `officer_ref`: backend-owned officer reference hash, not a real identity.
- `access_session_ref`: backend-owned unique access session reference.

The contract stores `bytes32` values, block timestamps, and writer addresses.
It never stores personally identifiable information or real case/file names.

## Private Network Options

Use Anvil for local unit and integration development. Use Besu QBFT for a
private integration/staging EVM network.

Besu QBFT stack:

```text
validator-1  validator-2  validator-3  validator-4
     |            |            |            |
     +------------+------------+------------+
                  private QBFT P2P network
                              |
                           rpc-node
                              |
                backend / blockchain_client
```

The Besu stack is under `network/besu`, pins `hyperledger/besu:26.7.0`, disables
validator RPC, binds RPC node HTTP to `127.0.0.1`, and exposes only `ETH`,
`NET`, and `WEB3`.

```powershell
cd network/besu
cp .env.example .env
bash scripts/generate-network.sh --force
bash scripts/start-network.sh
```

Do not call this production-ready until backup recovery, monitoring, security
review, host deployment, and external signer validation have passed on the
target environment.

## Contract API

`contracts/EvidenceRegistry.sol` exposes:

```solidity
function recordEvidence(bytes32 evidenceRef, bytes32 staticHash) external;
function recordAccess(bytes32 evidenceRef, bytes32 officerRef, bytes32 accessSessionRef) external;
function getEvidence(bytes32 evidenceRef) external view returns (bytes32, uint64, address, bool);
function getAccessBySession(bytes32 accessSessionRef) external view returns (bytes32, bytes32, uint64, address);
function evidenceExists(bytes32 evidenceRef) external view returns (bool);
function accessSessionExists(bytes32 accessSessionRef) external view returns (bool);
function pause() external;
function unpause() external;
```

## Roles

- `DEFAULT_ADMIN_ROLE`: grants and revokes roles.
- `WRITER_ROLE`: calls `recordEvidence` and `recordAccess`.
- `PAUSER_ROLE`: calls `pause` and `unpause`.

Use separate admin, backend writer, and validator/operator accounts. The
constructor requires a non-zero admin address and does not silently make
`msg.sender` the admin.

## Events

```solidity
event EvidenceRecorded(bytes32 indexed evidenceRef, bytes32 staticHash, uint64 recordedAt, address indexed writer);
event EvidenceAccessRecorded(bytes32 indexed evidenceRef, bytes32 indexed officerRef, bytes32 indexed accessSessionRef, uint64 recordedAt, address writer);
```

OpenZeppelin `Pausable` emits standard `Paused` and `Unpaused` events.

## Compile

```powershell
git clone --recurse-submodules https://github.com/Unsull/Blockchain.git
cd Blockchain
git submodule update --init --recursive
forge build
```

Foundry is pinned to `forge 1.7.1` in CI. Solidity dependencies are pinned by
Git submodules and `foundry.lock`; CI does not run `forge install`.

## Test

```powershell
forge fmt --check
forge build
forge test -vvv
forge test --gas-report
python -m pip install -e ".[dev]"
ruff check .
mypy blockchain_client
pytest -m "not integration" -vv
```

## Deploy

```powershell
$env:REGISTRY_ADMIN_ADDRESS="0x..."
$env:DEPLOYER_PRIVATE_KEY="0x..."
$env:CHAIN_ID="31337"
forge script script/DeployEvidenceRegistry.s.sol --rpc-url $env:RPC_URL --broadcast
```

Deployment scripts fail fast when `CHAIN_ID` does not match, the target contract
has no bytecode, or a role address is zero.

## Grant Or Revoke Writer

```powershell
$env:CONTRACT_ADDRESS="0x..."
$env:WRITER_ADDRESS="0x..."
$env:ADMIN_PRIVATE_KEY="0x..."
forge script script/GrantWriterRole.s.sol --rpc-url $env:RPC_URL --broadcast
forge script script/RevokeWriterRole.s.sol --rpc-url $env:RPC_URL --broadcast
```

Pauser role management uses `PAUSER_ADDRESS` with
`script/GrantPauserRole.s.sol` and `script/RevokePauserRole.s.sol`.

## Pause Or Unpause

```powershell
$env:CONTRACT_ADDRESS="0x..."
$env:PAUSER_PRIVATE_KEY="0x..."
forge script script/PauseRegistry.s.sol --rpc-url $env:RPC_URL --broadcast
forge script script/UnpauseRegistry.s.sol --rpc-url $env:RPC_URL --broadcast
```

## Python Client Usage

```python
from pathlib import Path
from blockchain_client import BlockchainClient, BlockchainClientSettings, LocalPrivateKeySigner

settings = BlockchainClientSettings(
    provider_uri="http://127.0.0.1:8545",
    chain_id=31337,
    contract_address="0x...",
    artifact_path=Path("out/EvidenceRegistry.sol/EvidenceRegistry.json"),
    confirmation_blocks=2,
)

signer = LocalPrivateKeySigner("0x...")
client = BlockchainClient(settings, signer=signer)
result = client.record_evidence(evidence_ref, static_hash)
access = client.record_access(evidence_ref, officer_ref, access_session_ref)
```

`signer_private_key` remains as a temporary backward-compatible setting, but new
integrations should inject a `TransactionSigner`. The client allocates nonces
from pending chain state, waits for configurable confirmations, validates the
emitted event against the input and receipt, and returns canonical lowercase
`0x`-prefixed bytes32 values.

## Environment Variables

- `RPC_URL`: Foundry script RPC URL.
- `REGISTRY_ADMIN_ADDRESS`: non-zero admin address for deployment.
- `DEPLOYER_PRIVATE_KEY`: deployment signer.
- `ADMIN_PRIVATE_KEY`: role-management signer.
- `PAUSER_PRIVATE_KEY`: pause/unpause signer.
- `CONTRACT_ADDRESS`: deployed registry address.
- `WRITER_ADDRESS`: backend writer address.
- `WRITER_PRIVATE_KEY`: writer signer key for local examples only.
- `UNAUTHORIZED_PRIVATE_KEY`: non-writer key for negative smoke tests.
- `MIN_CONFIRMATIONS`: client confirmation depth.
- `ARTIFACT_PATH`: Foundry artifact path.

The Python client accepts structured settings directly and does not read
secrets from global module state.

Use `.env.example` for production shape and `.env.anvil.example` only as local
Anvil scaffolding. Neither file contains private keys.

## Smoke Tests

After deploying and granting `WRITER_ROLE`, run:

```powershell
python .\examples\manual_smoke_test.py
python .\examples\manual_negative_smoke_test.py
```

The negative smoke test checks duplicate evidence, duplicate access session,
unauthorized writer rejection, and paused contract rejection.

## Deployment Manifests

Generate and verify manifests after deploy:

```powershell
python scripts/generate_deployment_manifest.py --network anvil --rpc-url $env:RPC_URL --chain-id 31337 --contract-address $env:CONTRACT_ADDRESS --deployer-address 0x... --admin-address $env:REGISTRY_ADMIN_ADDRESS --output deployments/anvil/EvidenceRegistry.manifest.json
python scripts/verify_deployment.py --manifest deployments/anvil/EvidenceRegistry.manifest.json
python scripts/export_artifact.py --output deployments/anvil/EvidenceRegistry.artifact.json
```

## Transaction Result Format

Python transaction submissions return:

- `tx_hash`
- `block_number`
- `block_timestamp` in UTC
- `contract_address`
- `chain_id`
- `confirmations`
- decoded event data

## Backend Integration Contract

Backend calls:

- `recordEvidence(evidence_ref: bytes32, static_hash: bytes32)`
- `recordAccess(evidence_ref: bytes32, officer_ref: bytes32, access_session_ref: bytes32)`

Backend remains responsible for authentication, user authorization,
real-identity mapping, evidence identity mapping, access session generation,
watermark logic, storage, databases, and proxy keys.

The blockchain module is responsible for contract authorization, signed
transaction submission, receipt validation, event decoding, transaction
verification, and chain state queries.

## Error Handling

The contract uses custom errors for invalid zero values, duplicates, missing
records, and invalid admin addresses. Python raises typed exceptions from
`blockchain_client.exceptions`; it does not swallow failures with `None`.

## Common Errors

### `artifact_path does not exist`

Cause: the contract has not been compiled yet.

Fix:

```powershell
forge build
```

The Python client expects this artifact by default:

```text
out/EvidenceRegistry.sol/EvidenceRegistry.json
```

### `no deployed bytecode at contract address`

Common causes:

- `CONTRACT_ADDRESS` is wrong.
- Anvil was restarted.
- The client is connected to a different chain.
- The contract has not been deployed.

Deploy the registry again and update `CONTRACT_ADDRESS`.

### `chain ID mismatch`

Check the active RPC chain:

```powershell
cast chain-id --rpc-url http://127.0.0.1:8545
```

For the local Anvil workflow this should return:

```text
31337
```

### `AccessControlUnauthorizedAccount`

Cause: the signer does not have `WRITER_ROLE`, `PAUSER_ROLE`, or
`DEFAULT_ADMIN_ROLE` for the action being attempted.

For writer transactions, run `GrantWriterRole.s.sol` with the admin key:

```powershell
$env:CONTRACT_ADDRESS="0x..."
$env:WRITER_ADDRESS="0x..."
$env:ADMIN_PRIVATE_KEY="0x..."
forge script script/GrantWriterRole.s.sol:GrantWriterRole --rpc-url $env:RPC_URL --broadcast -vvvv
```

### PowerShell activation is blocked

Allow activation for the current PowerShell process only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### `forge` not found

Close and reopen Git Bash, then run:

```bash
source ~/.bashrc
foundryup
forge --version
```

On Windows PowerShell, check whether the executable is on `PATH`:

```powershell
where.exe forge
forge --version
```

## Pull Request Workflow

After local tests pass, open a pull request:

```text
fix/blockchain-production-readiness -> main
```

Do not push directly to `main`. Require PR review and passing checks before
merge. Protect `main` with required status checks for `solidity` and `python`.

The PR URL is:

```text
https://github.com/Unsull/Blockchain/pull/new/fix/blockchain-production-readiness
```

GitHub Actions runs two jobs:

- `solidity`: uses recursive submodules, Foundry `1.7.1`, then runs
  `forge fmt --check`, `forge build`, `forge test -vvv`, and gas report.
- `python`: runs `ruff`, `mypy`, and `pytest -m "not integration" -vv`.
- `besu-network`: validates the Besu Docker Compose and network scripts without
  using real secrets.

Wait for both jobs to pass:

- Solidity CI: Passed
- Python CI: Passed

If no workflow appears in GitHub Actions, check that Actions are enabled for
the repository and that workflows from the feature branch are allowed to run.

## Migration

The previous root FastAPI demo was moved to `examples/legacy_api_example.py`.
See `MIGRATION.md` for breaking changes.
