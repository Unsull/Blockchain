# Transaction Verification Proofs

This directory stores runtime-generated JSON and Markdown verification proofs for the local
Besu integration/staging chain. Generated proof files are ignored by Git by default.

Proofs can contain public transaction hashes, contract addresses, sender addresses, and
opaque bytes32 references. Review every proof before sharing it. Opaque references must use
synthetic or backend-owned identifiers and must not contain real names or personal data.

Private keys and passwords are excluded from proof models and renderers by design. A proof
applies only to the configured chain and contract at its generation time. It is operational
verification evidence, not legal certification.
