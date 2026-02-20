# Artifact Persistence Contract - Bucket

## Storage Location
**Canonical Root:** `bucket/artifacts/`

## Artifact Structure
All decision artifacts MUST be persisted as JSON files with the following naming convention:
`{CATEGORY}_{TRACE_ID}_{TIMESTAMP}.json`

### Categories
- `success`: For requests that were successfully allowed.
- `failure`: For requests that were denied (expired, tampered, rate-limited, etc.).

## Schema Freeze (V1)
```json
{
  "metadata": {
    "trace_id": "UUID-V4",
    "category": "STRING",
    "timestamp": "ISO-8601 UTC"
  },
  "data": {
    "status": "allowed | denied",
    "reason": "STRING (optional for failure)",
    "identity": "STRING (optional for success)"
  }
}
```

## Reproducibility Rules
1. **Deterministic Naming:** The filename MUST include the `trace_id` recorded in telemetry to allow cross-system correlation.
2. **Immutable Persistence:** Once an artifact is written to the Bucket, it MUST NOT be modified.
3. **Fail-Closed Persistence:** If the Bucket is unavailable, the Bridge MUST emit a `degraded.state` telemetry event but MAY proceed with enforcement if configured for "Enforce-Then-Store" (current V1 behavior).
