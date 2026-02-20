🛡️ Sovereign Stack

Deterministic, Zero-Trust, Cryptographically Verified Multi-Service Architecture.

Overview

Sovereign Stack is a production-grade deterministic execution spine composed of:

Core – JWT Issuer (Port 5503)

Flow – Event Ingestor (Port 5502)

Bridge – Enforcement Gateway (Port 5500)

Bucket – Immutable Artifact Storage

The system guarantees:

Deterministic execution paths

Fail-closed security model

Cryptographic trust boundaries

Reproducibility from a clean environment

No hidden local dependencies

Architecture Flow

Client → Bridge → Core → Flow → Bucket

All communication occurs through frozen contracts. No implicit trust.

Setup
1. Create Virtual Environment
python -m venv venv

Activate (Windows Git Bash):

source venv/Scripts/activate
2. Install Dependencies
pip install -r requirements.txt
3. Start Full Stack
python start_all.py

Expected output:

All systems active.
Logs available in /logs/
Verification Matrix

Run deterministic validation:

python verification/day1_validation.py

Scenarios include:

Missing Token

Invalid Signature

Expired Token

Unauthorized Claims

Valid Success Path

System must fail-closed on all invalid scenarios.

Contracts

JWT_CONTRACT.md

TELEMETRY_CONTRACT.md

BUCKET_CONTRACT.md

CANONICAL_RUN.md

OBSERVABILITY.md

SOVEREIGN_STACK_PROOF.md

Reproducibility Validation

Spin up clean environment

Install dependencies

Run start_all.py

Execute verification matrix

Confirm identical results

Acceptance: No hidden local dependency. No nondeterministic behavior.

Security Guarantees

Strict JWT verification (RFC 7519)

Explicit failure states

No bypass paths

Deterministic logging

Immutable artifact persistence

Fail-closed under unexpected conditions
