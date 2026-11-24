# Local Docker infra

## Default stack

```bash
./docker-all-up.sh
# or: npm run local:containers:all:start
```

| Service | URL / port | Role |
|---------|------------|------|
| Redis | `localhost:6379` | Cache / sessions |
| Jaeger UI | http://localhost:16686 | Distributed traces |
| OTEL Collector | `localhost:4317` (gRPC), `:4318` (HTTP) | OTLP front door → Jaeger + Prometheus |

## Optional Postgres

```bash
./docker-all-up.sh --postgres
```

## AIOps / LLMOps / DataOps (`--observability`)

```bash
./docker-all-up.sh --observability
# or: npm run local:containers:all:start:observability
```

| Domain | Service | URL | What you get |
|--------|---------|-----|----------------|
| **AIOps** | Prometheus | http://localhost:9090 | Time-series scrape of LLM + collector metrics |
| **AIOps** | Grafana | http://localhost:3000 (`admin`/`admin`) | Dashboard **Council LLMOps Overview** |
| **LLMOps** | Phoenix | http://localhost:6006 | Generations, spans, latency inspection |
| **DataOps** | Loki | http://localhost:3100 | Log aggregation (wire app logs later) |

### LLMOps metrics the app records

From `Middleware/Observability/llmops.py` after `setup_observability()`:

| Metric | Meaning |
|--------|---------|
| `council_llm_requests_total` | Generations by agent / model / status / wave |
| `council_llm_tokens_total` | Prompt vs completion tokens |
| `council_llm_cost_usd_total` | Estimated USD cost (rate table + env overrides) |
| `council_llm_duration_seconds` | End-to-end generation latency histogram |
| `council_llm_ttft_seconds` | Time-to-first-token histogram |
| OTEL spans `llm.<agent>` | Timestamps, tokens, cost, wave, session_id |

App Prometheus scrape target (host): http://localhost:9108/metrics

### Combine flags

```bash
./docker-all-up.sh --postgres --observability
```

### Stop

```bash
./docker-all-down.sh
# wipe volumes: ./docker-all-down.sh --volumes
```
