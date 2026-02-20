# Telemetry Surface Contract - InsightFlow

## Endpoint Specification
- **URL:** `http://localhost:5002/ingest`
- **Method:** `POST`
- **Content-Type:** `application/json`

## Authentication
- **Mechanism:** JWT Authorization Header
- **Issuer Required:** `bhiv-core-authority`
- **Scope Required:** `telemetry:write`

## Schema Freeze (V1)
All events MUST follow this structure:
```json
{
  "timestamp": "ISO-8601 UTC",
  "event_type": "STRING",
  "source": "STRING",
  "trace_id": "UUID-V4",
  "payload": {
    "..."
  }
}
```

## Mandatory Event Types
- `request.received`: Emitted immediately upon Bridge receiving a request.
- `auth.success`: Emitted after successful JWT verification.
- `auth.failure`: Emitted after failed JWT verification (includes reason).
- `decision.made`: Emitted when the bridge finalizes the request handling.
- `degraded.state`: Emitted when external dependencies (Bucket, Core) are unreachable.

## Validation Rules
1. **Immutable Timestamps:** Events with future or excessive past timestamps (>5m) are rejected.
2. **Schema Enforcement:** Payloads not matching the event_type schema are dropped.
3. **Traceability:** `trace_id` MUST be propagated from the initial `request.received` through all subsequent events in the same chain.
