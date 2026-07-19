# Private Network Security Checklist

- Pin and document the exact Geth version.
- Validate genesis compatibility with the selected consensus mode.
- Separate validator and RPC node duties.
- Restrict RPC ingress to backend networks.
- Expose only `eth`, `net`, and `web3` namespaces.
- Disable account unlocking on RPC nodes.
- Store private keys outside the repository.
- Monitor peer count, block height, disk usage, and RPC errors.
- Back up node keys and chain data according to recovery objectives.
- Test multi-node behavior before calling the network production-ready.
