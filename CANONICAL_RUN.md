# Canonical Execution Guide - Sovereign Stack

## Startup Sequence
The stack MUST be started in the following order to ensure dependency availability:

1. **Core JWT Authority** (Port 5503)
   - Provides public keys and mints tokens for internal service communication.
2. **InsightFlow Telemetry Surface** (Port 5502)
   - Must be live before Bridge starts emitting events.
3. **InsightBridge Security Enforcer** (Port 5500)
   - The primary gateway.

### Command
```bash
python start_all.py
```

## Shutdown Sequence
To shut down the stack safely and ensure all telemetry is flushed and nonces saved:
1. Send `SIGINT` (Ctrl+C) to the `start_all.py` process.
2. The orchestrator will propagate `SIGTERM` to sub-services.

## Idempotent Restart Proof
The system tracks state in:
- `bridge/seen_nonces.json`: Persists replay protection across restarts.
- `flow/data/`: Telemetry logs.
- `bucket/artifacts/`: Permanent decision artifacts.

## Verification
After startup, run the verification matrix:
```bash
python verification/day1_validation.py
```
Expected output: All scenarios return `PASS`.
All logs are captured in `./logs/`.
