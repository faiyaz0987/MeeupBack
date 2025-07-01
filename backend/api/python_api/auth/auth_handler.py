import jwt
from datetime import datetime, timedelta

SECRET_KEY = "supersecretkey"  # You can load from env later

def sign_jwt(uid: str) -> dict:
    payload = {
        "uid": uid,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"access_token": token}

def decode_jwt(token: str) -> dict:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded if decoded["exp"] >= datetime.utcnow().timestamp() else None
    except:
        return None
