# Besu QBFT Monitoring Dashboard

## Purpose

The **Besu QBFT Private Network Overview** dashboard provides operational visibility for
the integration/staging network. It monitors node availability, chain progress, peer
connectivity, transaction-pool state, JVM resources, and inferred network health. It does
not expose evidence records, officer identities, secrets, or validator keys.

## Architecture

```text
Besu validator and RPC metrics -> Prometheus -> Grafana
```

Prometheus scrapes all four validators and the RPC node every 15 seconds. Grafana uses the
provisioned Prometheus datasource with UID `prometheus`.

## Start Monitoring

From the repository root, run:

```bash
docker compose \
  --project-directory network/besu \
  --env-file network/besu/.env \
  -f network/besu/docker-compose.yml \
  -f network/besu/docker-compose.monitoring.yml \
  up -d
```

The local endpoints are:

- Grafana: <http://127.0.0.1:3000>
- Prometheus: <http://127.0.0.1:9090>
- Besu RPC: <http://127.0.0.1:8545>

These host ports bind only to `127.0.0.1`. Validator RPC ports are not published.

## Grafana Credentials

The administrator username comes from `GRAFANA_ADMIN_USER` and the password comes from
`GRAFANA_ADMIN_PASSWORD` in `network/besu/.env`. Change the password in that ignored local
file before starting Grafana. Do not commit the value. If the Grafana data volume already
contains an administrator account, changing the environment variable does not replace the
stored password; use Grafana's administrator password-reset procedure instead.

## Verify Prometheus Targets

Open <http://127.0.0.1:9090/targets> or query:

```bash
curl http://127.0.0.1:9090/api/v1/targets
```

The targets `validator-1:9545` through `validator-4:9545` and `rpc-node:9545` should all be
`UP`. Target health proves that Prometheus can scrape metrics; it does not prove consensus
participation.

## Locate the Dashboard

Sign in to Grafana, open **Dashboards**, select the **Besu** folder, and open **Besu QBFT
Private Network Overview**. Provisioning uses UID `besu-qbft-overview`, so the direct path
is `/d/besu-qbft-overview` after Grafana starts.

## Dashboard Sections

### Network Overview

Shows the number of reachable Besu targets and validators, RPC target state, maximum block
height, RPC peer count, and RPC synchronization state. A healthy baseline is five Besu
targets and four validator targets. The live Besu 26.7.0 discovery observed
`besu_synchronizer_in_sync=1` for an in-sync node.

### Blockchain Activity

Shows block height by node, derived block rate, estimated block interval, current
transaction-pool size, transactions in the chain-head block, and active RPC HTTP
connections. Block rate and interval use a five-minute range and can be distorted during
startup, scrape gaps, or a stall. A very large interval signals near-zero progress; it is
not forced to look normal.

### Node Resources

Shows resident process memory, JVM heap and non-heap memory areas, process CPU cores, JVM
threads, open file descriptors, and garbage-collection event/time rates. CPU is process
CPU, not host percentage. JVM memory areas and garbage collectors remain separate series.

### Consensus and Network Health

Shows block-height divergence, peers by node, availability history, an inferred block-stall
state, and QBFT timer executor threads. Block-height divergence is the difference between
the highest and lowest monitored node heights. Zero is aligned; one can occur briefly near
a scrape boundary; sustained values of two or more require investigation.

The stall indicator reports `STALLED` when the RPC node height has not increased over one
minute. The window covers multiple five-second block periods and four 15-second scrape
intervals, reducing normal scrape-boundary false positives. Startup, missing samples, or
RPC target failure still require checking target health and logs.

### Monitoring Health

Shows scrape state by node and whether process resident memory exceeds the existing 1.5 GB
alert threshold. The dashboard comparison is immediate; the Prometheus alert rule applies
its configured `for` duration before firing.

## Metric Semantic Warnings

- Block height is chain progress, not evidence count or transaction count.
- Chain-head transaction count describes the current head block, not a cumulative total.
- Transaction-pool size is pending work at a node, not confirmed transactions.
- Peer count measures direct P2P connections. It is not QBFT quorum because the RPC node's
  direct topology does not describe validator voting relationships.
- Validator target availability does not prove participation in the current QBFT round.
- QBFT timer executor threads are internal work activity, not votes, quorum, or consensus
  success.
- Block-height divergence and block-stall state are inferred indicators, not direct QBFT
  telemetry.

## Why Evidence Count Is Not Available

Besu 26.7.0 process metrics do not expose application-level EvidenceRegistry record counts.
An evidence count requires a trusted application index, decoded contract events, or a
purpose-built read model. Reusing block height or transaction count would be semantically
incorrect, so the dashboard intentionally omits Total Evidence and Total Access panels.

## Why Grafana Is Not Transaction Proof

Grafana aggregates time-series process metrics and is not a blockchain explorer. It cannot
prove an individual transaction, its calldata, emitted events, or resulting contract state.
Verify transaction correctness with the receipt, decoded events, block inclusion, and
contract reads against the expected chain and contract address.

## Export a Panel Image

Open a panel menu and select **Share**, then use the image/render option available in the
local Grafana installation. A rendered-image export may require Grafana's image-renderer
component; without it, capture the panel through the browser or export its data instead.
Never include credentials or sensitive browser content in screenshots.

## Export Prometheus Query Results

Use Prometheus **Graph** view and download CSV where available, or save the HTTP API JSON:

```bash
curl --get http://127.0.0.1:9090/api/v1/query \
  --data-urlencode 'query=ethereum_blockchain_height{job="besu"}' \
  --output block-height.json
```

For research exports, record the UTC timestamp, query, range, step, Besu version, and chain
configuration alongside the data. Metrics are operational observations, not evidence-chain
records.

## Stop Without Deleting Volumes

```bash
docker compose \
  --project-directory network/besu \
  --env-file network/besu/.env \
  -f network/besu/docker-compose.yml \
  -f network/besu/docker-compose.monitoring.yml \
  down
```

Do not add `-v`. The command above preserves validator, RPC, Prometheus, and Grafana named
volumes.

## Known Limitations

- No direct QBFT quorum, validator-vote, or round-success metric was discovered.
- Inferred health cannot identify which validator caused a stalled round.
- Five-minute rate panels need enough samples after startup.
- One-minute stall detection trades fast detection for fewer scrape-timing false positives.
- Prometheus retention is local and depends on the persistent volume and storage settings.
- No application-level evidence/access totals or individual transaction inspection exists.
- This configuration has no external authentication or TLS and is localhost-only.

## Classification

This dashboard is **Integration/Staging Only**. It is not a production monitoring, auditing,
forensics, or transaction-proof system.
