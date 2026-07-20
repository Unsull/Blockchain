# Failure Testing

The scripted subset is:

- stop `validator-4`; block production must continue
- stop `validator-3` and `validator-4`; block production must halt
- restart validators; block production must resume

Run:

```bash
python network/besu/scripts/failure-test.py --rpc-url http://127.0.0.1:8545
```

Record JSON output from `network/besu/logs/failure-test-results.json`.

Additional manual scenarios:

- stop `rpc-node`; validators continue producing blocks
- restart `rpc-node`; it syncs back
- `docker compose down` followed by `up -d`; volumes retain chain data
- remove `rpc-node` volume; it resyncs from validators
- revoke `WRITER_ROLE`; write transaction fails
- pause the contract; write transaction fails; unpause restores writes
