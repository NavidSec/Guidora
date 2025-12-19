import os
import logging
import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.database import User, Specialties
from bson import ObjectId 

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
        obj_id = ObjectId(uid)
        
        user_obj = User.objects(id=obj_id, token=token).first() or \
                   Specialties.objects(id=obj_id, token=token).first()

        if not user_obj:
            debug_user = User.objects(id=obj_id).first()
            if debug_user:
                logger.warning(f"User {uid} found, but TOKEN in DB is different from what Android sent!")
            else:
                logger.warning(f"No user found with ID: {uid}")
            
            raise HTTPException(status_code=401, detail="Invalid UID or Token")

        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"ok": True}

    except Exception as e:
        logger.error(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")