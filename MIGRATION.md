# Migration Notes

This module replaces the previous demo-oriented implementation with a production
blockchain boundary.

## Breaking Changes

- `watermarkHash` is now `staticHash`.
- string identifiers are now `bytes32` references.
- `accessHash` was removed.
- `actionType` is not part of the contract.
- `accessSessionId` is now `accessSessionRef`.
- `getAccessLogs` unbounded array reads were removed.
- unlocked account transaction submission was removed.
- hard-coded ABI strings were removed from Python source.
- FastAPI demo endpoints are not part of the core module.
- forensic watermark naming was replaced by transaction verification.
- AES encryption is not part of this blockchain module.

## Legacy Demo

The old API shape is preserved only as a marker in
`examples/legacy_api_example.py`. Production backend integrations should use the
Python client package and keep officer identity mapping in backend storage.

## Contract Versioning

The registry is intentionally immutable. Schema changes should deploy a new
contract version and update the backend configuration to point at the new
address. Historical verification should keep the old artifact and address.
