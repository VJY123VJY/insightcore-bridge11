from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import requests
import uuid
import datetime
import os
import json
from bucket.store import BucketStore

app = FastAPI(title="InsightBridge - Sovereign Enforcer")
auth_scheme = HTTPBearer()

# Configuration
CORE_PUBLIC_KEY_PATH = "core/keys/public.pem"
FLOW_INGEST_URL = "http://127.0.0.1:5502/ingest"
NONCE_DB = "bridge/seen_nonces.json"

# Rate limiting
RATE_LIMIT = {} # identity -> [count, last_reset]
MAX_REQUESTS = 5
WINDOW = 60

bucket = BucketStore()

# Load public key
with open(CORE_PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()

# Nonce tracking
if os.path.exists(NONCE_DB):
    try:
        with open(NONCE_DB, "r") as f:
            SEEN_NONCES = set(json.load(f))
    except:
        SEEN_NONCES = set()
else:
    SEEN_NONCES = set()

def save_nonces():
    with open(NONCE_DB, "w") as f:
        json.dump(list(SEEN_NONCES), f)

def emit_telemetry(event_type, source, trace_id, payload, token=None):
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "source": source,
        "trace_id": trace_id,
        "payload": payload
    }
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        # In a real system, this would be async/buffered
        requests.post(FLOW_INGEST_URL, json=event, headers=headers, timeout=2)
    except Exception as e:
        print(f"TELEMETRY ERROR: {str(e)}")

@app.post("/enforce")
async def enforce(request: Request, credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    trace_id = str(uuid.uuid4())
    token_str = credentials.credentials
    
    # Event: request.received
    emit_telemetry("request.received", "bridge", trace_id, {"method": "POST", "path": "/enforce"}, token_str)

    try:
        # 1. JWT Validation
        payload = jwt.decode(
            token_str, 
            PUBLIC_KEY, 
            algorithms=["RS256"],
            audience="bhiv-sovereign-spine",
            issuer="bhiv-core-authority",
            leeway=0 # Strict enforcement
        )
        
        # 2. Nonce Validation (Replay Protection)
        nonce = payload.get("nonce")
        if not nonce:
            raise jwt.InvalidTokenError("Missing nonce")
        
        if nonce in SEEN_NONCES:
            raise jwt.InvalidTokenError("Replay attempt detected (nonce reuse)")
        
        SEEN_NONCES.add(nonce)
        save_nonces()
        
        # 3. Rate Limit Validation
        identity = payload['sub']
        now = datetime.datetime.utcnow().timestamp()
        if identity not in RATE_LIMIT:
            RATE_LIMIT[identity] = [1, now]
        else:
            count, last_reset = RATE_LIMIT[identity]
            if now - last_reset > WINDOW:
                RATE_LIMIT[identity] = [1, now]
            else:
                if count >= MAX_REQUESTS:
                    emit_telemetry("auth.failure", "bridge", trace_id, {"reason": "rate_limit_exceeded"}, token_str)
                    raise jwt.InvalidTokenError("Rate limit exceeded")
                RATE_LIMIT[identity][0] += 1

        # Event: auth.success
        emit_telemetry("auth.success", "bridge", trace_id, {"sub": payload['sub'], "nonce": nonce}, token_str)
        
        # 4. Decision
        decision = {"status": "allowed", "trace_id": trace_id, "identity": payload['sub']}
        emit_telemetry("decision.made", "bridge", trace_id, decision, token_str)
        
        # Artifact Persistence
        bucket.persist_artifact(trace_id, "success", decision)
        
        return decision

    except jwt.ExpiredSignatureError:
        emit_telemetry("auth.failure", "bridge", trace_id, {"reason": "expired"}, token_str)
        bucket.persist_artifact(trace_id, "failure", {"reason": "expired"})
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        emit_telemetry("auth.failure", "bridge", trace_id, {"reason": str(e)}, token_str)
        bucket.persist_artifact(trace_id, "failure", {"reason": str(e)})
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        emit_telemetry("degraded.state", "bridge", trace_id, {"error": str(e)}, token_str)
        raise HTTPException(status_code=500, detail="Internal Safety Breach")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5500)
