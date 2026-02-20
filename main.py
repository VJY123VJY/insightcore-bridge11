from fastapi import FastAPI
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

PRIVATE_KEY = """-----BEGIN PRIVATE KEY-----
YOUR_PRIVATE_KEY_HERE
-----END PRIVATE KEY-----"""

ALGORITHM = "RS256"

@app.post("/issue")
def issue_token():
    payload = {
        "sub": "vijay",
        "exp": datetime.utcnow() + timedelta(minutes=60)
    }

    token = jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)

    return {"access_token": token}