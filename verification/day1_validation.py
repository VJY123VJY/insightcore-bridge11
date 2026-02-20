import requests
import time
import json
import os
import jwt

CORE_URL = "http://127.0.0.1:5503"
BRIDGE_URL = "http://127.0.0.1:5500"
FLOW_URL = "http://127.0.0.1:5502"

def log_scenario(name, result, detail=""):
    print(f"[SCENARIO] {name}: {'PASS' if result else 'FAIL'} - {detail}")

def run_tests():
    # 0. Missing Token
    print("Scenario 0: Missing Token")
    resp = requests.post(f"{BRIDGE_URL}/enforce")
    # FastAPI returns 403 Forbidden for missing credentials in Depends(HTTPBearer()) if not specified otherwise
    log_scenario("Missing Token", resp.status_code in [401, 403], resp.text)

    # 1. Success Path
    print("Scenario 1: Valid Core Token")
    resp = requests.post(f"{CORE_URL}/issue", json={"sub": "user_123", "scope": "telemetry:write"})
    token = resp.json()['access_token']
    
    resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {token}"})
    log_scenario("Valid Token", resp.status_code == 200, resp.text)

    # 2. Failure: Expired Token
    print("Scenario 2: Expired Token")
    # Using 0 leeway now, so -10 should fail.
    resp = requests.post(f"{CORE_URL}/issue", json={"sub": "user_123", "scope": "telemetry:write", "expiry_seconds": -10})
    token_exp = resp.json()['access_token']
    resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {token_exp}"})
    log_scenario("Expired Token", resp.status_code == 401, resp.text)

    # 3. Failure: Tampered Signature
    print("Scenario 3: Tampered Signature")
    tampered_token = token[:-5] + "aaaaa"
    resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {tampered_token}"})
    log_scenario("Tampered Token", resp.status_code == 401, resp.text)

    # 4. Failure: Wrong Issuer (Mocked)
    print("Scenario 4: Wrong Issuer")
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization
    
    private_key_fake = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_fake = private_key_fake.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    payload_fake = {
        "iss": "fake-issuer",
        "aud": "bhiv-sovereign-spine",
        "sub": "attacker",
        "iat": time.time(),
        "exp": time.time() + 3600,
        "nonce": "unique-fake-nonce",
        "scope": "telemetry:write"
    }
    token_fake = jwt.encode(payload_fake, pem_fake, algorithm="RS256")
    resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {token_fake}"})
    log_scenario("Wrong Issuer", resp.status_code == 401, resp.text)

    # 5. Failure: Replay Nonce
    print("Scenario 5: Replay Nonce")
    resp = requests.post(f"{CORE_URL}/issue", json={"sub": "user_123", "scope": "telemetry:write"})
    token_replay = resp.json()['access_token']
    requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {token_replay}"})
    resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {token_replay}"})
    log_scenario("Replay Nonce", resp.status_code == 401 and "Replay" in resp.text, resp.text)

    # 6. Failure: Rate Limit
    print("Scenario 6: Rate Limit")
    for i in range(10):
        resp = requests.post(f"{CORE_URL}/issue", json={"sub": "limit_user", "scope": "telemetry:write"})
        t = resp.json()['access_token']
        resp = requests.post(f"{BRIDGE_URL}/enforce", headers={"Authorization": f"Bearer {t}"})
        if resp.status_code == 401 and "Rate limit" in resp.text:
            log_scenario("Rate Limit", True, f"Blocked at attempt {i+1}")
            break
    else:
        log_scenario("Rate Limit", False, "Did not block after 10 attempts")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"VERIFICATION ERROR: {str(e)}")
