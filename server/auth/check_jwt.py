import os
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.database import User, Specialties
import jwt

router = APIRouter()
logger = logging.getLogger("auth.check_jwt")

JWT_SECRET: str = os.getenv("GUIDORA_JWT_SECRET")
if not JWT_SECRET:
    logger.critical("Environment variable GUIDORA_JWT_SECRET is not set. Aborting startup.")
    raise RuntimeError("Missing required environment variable: GUIDORA_JWT_SECRET")

JWT_ALGORITHM = os.getenv("GUIDORA_JWT_ALGO", "HS256")

class AuthCheckRequest(BaseModel):
    uid: str
    token: str

@router.post("/check_jwt")
async def check_jwt(payload: AuthCheckRequest):
    uid = payload.uid.strip()
    token = payload.token.strip()

    if not uid or not token:
        raise HTTPException(status_code=400, detail="uid and token are required")

    user_obj = User.objects(uid=uid, token=token).first() \
               or Specialties.objects(uid=uid, token=token).first()

    if not user_obj:
        raise HTTPException(status_code=401, detail="UID or token not found")

    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"ok": True}
