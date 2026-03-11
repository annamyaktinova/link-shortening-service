from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from config import SECRET

security = HTTPBearer()


async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    if credentials is None:
        return None 

    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            return None
        return {"id": int(user_id), "username": payload.get("username")}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")