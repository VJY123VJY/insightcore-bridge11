# JWT Cryptographic Contract - Sovereign Stack

## Authority
**Canonical Issuer:** `bhiv-core-authority`
**Audience:** `bhiv-sovereign-spine`

## Cryptographic Parameters
- **Algorithm:** RS256 (RSA Signature with SHA-256)
- **Key Rotation Policy:** Static for V1 Integration.
- **Public Key (PEM):** (To be generated and stored in `/core/keys/public.pem`)

## Token Policy
- **Expiry (exp):** T + 3600 seconds (1 hour)
- **Not Before (nbf):** T - 60 seconds
- **Issued At (iat):** T
- **Nonce (nonce):** Required for all tokens to prevent replay.

## Claims Schema
| Claim | Required | Value / Pattern |
|-------|----------|-----------------|
| `iss` | Yes | `bhiv-core-authority` |
| `aud` | Yes | `bhiv-sovereign-spine` |
| `sub` | Yes | Identity identifier (e.g., `service:flow`) |
| `exp` | Yes | NumericDate |
| `iat` | Yes | NumericDate |
| `nonce`| Yes | UUID v4 |
| `scope`| Yes | Space-separated list of permissions |

## Enforcement Rules
1. **Signature Validation:** Bridge MUST validate the RS256 signature against the Core Public Key.
2. **Issuer Check:** `iss` MUST match canonical issuer.
3. **Audience Check:** `aud` MUST match canonical audience.
4. **Time Window:** Current time MUST be between `nbf` and `exp`.
5. **Nonce Check:** Bridge MUST track seen nonces and refuse duplicates (Fail-Closed).
