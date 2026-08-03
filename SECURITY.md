# Security Policy

## Supported Versions

Security fixes target the current `0.1.x` blockchain module.

## Reporting A Vulnerability

Report vulnerabilities privately to the repository maintainers. Do not open a
public issue with exploit details, private keys, RPC URLs, or chain credentials.

## Secret Handling

Never commit deployer, admin, pauser, or writer private keys. Use environment
variables or a secret manager for deployment automation. The Python client signs
raw transactions locally and should run only in a controlled backend execution
environment.

Prefer injecting a signer implementation instead of storing a private key in
application settings. `signer_private_key` is kept only for migration
compatibility and should not be used for new production integrations.

## RPC Exposure

Expose only the RPC namespaces required by backend integration: `eth`, `net`,
and `web3`. Do not expose `personal`, `admin`, `debug`, `trace`, `txpool`,
`qbft`, `perm`, or `miner` to backend systems or external networks.

The Besu QBFT stack binds RPC to `127.0.0.1` on the Docker host. Validators have
RPC disabled and use generated static peers with discovery disabled.

## Signer Security

Use separate accounts for deployer, admin, pauser, backend writer, and
validator/operator duties. Validator keys must not be reused as deployer,
admin, pauser, or writer keys. Store admin keys offline when possible. Rotate
writer keys by granting a new writer and revoking the old writer.

Deployment automation should generate a manifest and verify bytecode, chain ID,
contract address, and role assignments before enabling backend writes.

## Admin Key Recommendations

Use a multisig or offline process for `DEFAULT_ADMIN_ROLE` in production-like
environments. The admin account should not submit routine evidence or access
transactions.
