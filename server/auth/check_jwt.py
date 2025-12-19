import os
import logging
import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.database import User, Specialties

router = APIRouter()
logger = logging.getLogger("auth.check_jwt")

JWT_SECRET = os.getenv("GUIDORA_JWT_SECRET")
JWT_ALGORITHM = os.getenv("GUIDORA_JWT_ALGO", "HS256")

class AuthCheckRequest(BaseModel):
    uid: str
    token: str

@router.post("/check_jwt")
async def check_jwt(payload: AuthCheckRequest):
    uid = payload.uid.strip()
    token = payload.token.strip()

    try:
        user_obj = User.objects(uid=uid, token=token).first() or \
                   Specialties.objects(uid=uid, token=token).first()

        if not user_obj:
            debug_user = User.objects(uid=uid).first() or Specialties.objects(uid=uid).first()
            if debug_user:
                logger.warning(f"User {uid} found, but TOKEN in DB is different!")
            else:
                logger.warning(f"No user found with UID: {uid}")
            
            raise HTTPException(status_code=401, detail="Invalid UID or Token")

        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        return {"ok": True}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    except Exception as e:
        logger.error(f"Auth error: {str(e)}") 
        raise HTTPException(status_code=401, detail="Authentication failed")