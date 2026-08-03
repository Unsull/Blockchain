# Backup And Recovery

Back up:

- `genesis/genesis.json`
- generated validator keys from secure storage
- `build/static-nodes.json`
- `nodes/*/config.toml`
- `docker-compose.yml`
- deployment manifests and exported artifacts
- role state for admin, pauser, and writer accounts
- monitoring configuration

Recovery flow:

1. Restore genesis and static peers.
2. Restore the validator key for the replacement node.
3. Start the replacement node with the same config.
4. Confirm peer connectivity.
5. Wait for chain sync.
6. Validate block height.
7. Validate validator set and quorum.
8. Validate `EvidenceRegistry` bytecode at the recorded address.
9. Validate roles.
10. Run health check and smoke test.

Required drills before production claims:

- Delete `rpc-node` data volume and confirm it syncs from validators.
- Delete `validator-4` data while keeping its key, then confirm it rejoins and
  syncs.

Do not claim these drills have passed until they have been run on the target
host.
