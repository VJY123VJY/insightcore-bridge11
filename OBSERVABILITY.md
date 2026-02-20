# Observability and Failure Transparency - Sovereign Stack

## Log Formats
Standard logging is captured in `/logs/`:
- `core.log`: Core JWT Authority events.
- `flow.log`: Telemetry ingestion events.
- `bridge.log`: Traffic enforcement and decision events.

## No Secret Leakage Guarantee
1. **JWT Bodies Only:** Logs capture JWT claims (non-sensitive identity/scopes).
2. **No Signatures/Keys:** RSA Private keys and full JWT signatures are EXCLUDED from all flow and bridge logs.
3. **Redacted Payloads:** Application-specific request bodies are not logged by the Bridge; only metadata (path, method) is emitted.

## Degraded States
The stack identifies and signals the following explicit states:
- **`TELEMETRY ERROR`**: Printed to Bridge logs when `Flow` is unreachable.
- **`Internal Safety Breach`**: 500 status returned when an unhandled exception occurs in the enforcer logic.
- **`Not authenticated`**: 401 status when credentials are missing or malformed.

## Verification Matrix Results
The current stack has been verified against the Following Execution Matrix:

| Scenario | Expected Bridge Status | Telemetry Recorded | Bucket Artifact | Result |
|----------|------------------------|--------------------|-----------------|--------|
| Valid JWT | 200 OK | Yes | success | PASS |
| Expired JWT | 401 Unauthorized | Yes | failure | PASS |
| Tampered JWT| 401 Unauthorized | Yes | failure | PASS |
| Replay Attempt| 401 Unauthorized | Yes | failure | PASS |
| Rate Limit | 401 Unauthorized | Yes | failure | PASS |
| Wrong Issuer | 401 Unauthorized | Yes | failure | PASS |
