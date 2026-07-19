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

## RPC Exposure

Expose only the RPC namespaces required by backend integration: `eth`, `net`,
and `web3`. Do not expose `personal`, `admin`, `debug`, or `miner` to backend
systems or external networks.

## Signer Security

Use separate accounts for deployer, admin, pauser, backend writer, and
validator/operator duties. Store admin keys offline when possible. Rotate writer
keys by granting a new writer and revoking the old writer.

## Admin Key Recommendations

Use a multisig or offline process for `DEFAULT_ADMIN_ROLE` in production-like
environments. The admin account should not submit routine evidence or access
transactions.
