from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt
import datetime
import uuid
import os

app = FastAPI(title="Sovereign Core - JWT Authority")

# Load keys
PRIVATE_KEY_PATH = "core/keys/private.pem"
PUBLIC_KEY_PATH = "core/keys/public.pem"

with open(PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()

with open(PUBLIC_KEY_PATH, "r") as f:
    PUBLIC_KEY = f.read()

ISSUER = "bhiv-core-authority"
AUDIENCE = "bhiv-sovereign-spine"

class TokenRequest(BaseModel):
    sub: str
    scope: str
    expiry_seconds: int = 3600

@app.get("/public-key")
async def get_public_key():
    return {"public_key": PUBLIC_KEY}

@app.post("/issue")
async def issue_token(req: TokenRequest):
    payload = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "sub": req.sub,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=req.expiry_seconds),
        "nonce": str(uuid.uuid4()),
        "scope": req.scope
    }
    token = jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")
    return {"access_token": token, "token_type": "bearer"}

if __name__ == "__main__":
    import uvicorn
    try:
        uvicorn.run(app, host="127.0.0.1", port=5503)
    except Exception as e:
        print(f"CORE STARTUP ERROR: {e}")
