from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import json
import os
from datetime import datetime

app = FastAPI(title="InsightFlow - Telemetry Ingestion")
auth_scheme = HTTPBearer()

# Load public key from core (in a real system, would be fetched or cached)
PUBLIC_KEY_PATH = "core/keys/public.pem"
with open(PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()

ISSUER = "bhiv-core-authority"
AUDIENCE = "bhiv-sovereign-spine"

# Simple storage for verification
STORAGE_DIR = "flow/data"
os.makedirs(STORAGE_DIR, exist_ok=True)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    try:
        payload = jwt.decode(
            credentials.credentials, 
            PUBLIC_KEY, 
            algorithms=["RS256"],
            audience=AUDIENCE,
            issuer=ISSUER,
            leeway=0
        )
        if "telemetry:write" not in payload.get("scope", ""):
            raise HTTPException(status_code=403, detail="Insufficient scope")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

@app.post("/ingest")
async def ingest(request: Request, token: dict = Depends(verify_token)):
    try:
        data = await request.json()
        # Basic schema validation
        required_fields = ["timestamp", "event_type", "source", "trace_id", "payload"]
        if not all(field in data for field in required_fields):
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Store deterministically
        filename = f"{STORAGE_DIR}/{data['trace_id']}_{data['event_type']}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
            
        print(f"STORED: {data['event_type']} from {data['source']} (Trace: {data['trace_id']})")
        return {"status": "success", "id": data['trace_id']}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5502)
