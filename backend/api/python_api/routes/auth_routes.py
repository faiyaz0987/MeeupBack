from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.python_api.auth.auth_handler import sign_jwt
from api.python_api.dependencies.db_loader import get_db_sync

router = APIRouter()

class LoginModel(BaseModel):
    username: str
    password: str  # SHA256 hashed input

@router.post("/login")
def login(user: LoginModel):
    db = get_db_sync()
    cursor = db.mysql_cursor
    query = """
        SELECT uid FROM admin WHERE username = %s AND password = %s
        UNION
        SELECT uid FROM host_participant WHERE username = %s AND password = %s
    """
    cursor.execute(query, (user.username, user.password, user.username, user.password))
    result = cursor.fetchone()
    if result:
        uid = result[0]
        return sign_jwt(uid)
    raise HTTPException(status_code=401, detail="Invalid credentials")
