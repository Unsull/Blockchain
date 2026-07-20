# Besu QBFT Architecture

The integration/staging topology uses four validator nodes and one separate RPC
node. Validators participate in QBFT consensus and do not expose HTTP or WS RPC
to the host. The RPC node peers with the validators and exposes only JSON-RPC
HTTP on `127.0.0.1:${RPC_HTTP_PORT}`.

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

Consensus tolerates one failed validator in a four-validator network. With two
validators offline, block production should halt until quorum is restored.

This network is intended for integration and staging. It is not production-ready
until backup recovery, monitoring, security review, host deployment, and
external signer validation are completed.
