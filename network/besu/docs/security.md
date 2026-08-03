# Besu Network Security

- RPC is bound to localhost on the Docker host.
- Validators do not expose HTTP or WS RPC.
- RPC node exposes only `ETH`, `NET`, and `WEB3`.
- `ADMIN`, `DEBUG`, `TRACE`, `TXPOOL`, `QBFT`, `PERM`, account management, and
  unlocked account APIs are not exposed.
- Discovery is disabled; peers come from generated static nodes.
- No wildcard CORS is configured.
- Node keys, validator keys, `.env`, runtime data, logs, and generated keystores
  are ignored by Git.
- Validator keys must not be reused as deployer, admin, pauser, or writer keys.
- Admin accounts should not be routine writers.
- Use a reverse proxy with TLS and firewall allowlists for staging hosts.
- Use a secret manager or injected environment for deployer/admin/writer keys.
- Rotate writer keys by granting a new writer and revoking the old writer.
- Keep `hyperledger/besu` pinned to an exact version, and test upgrades in a new
  chain or full staging clone.
- Encrypt backups containing validator keys and deployment manifests.
