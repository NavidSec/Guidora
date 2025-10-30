# auth/verify_otp.py
import os
from datetime import datetime, timedelta
import logging
from typing import Optional

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.db import User, Specialties

router = APIRouter()
logger = logging.getLogger("auth.verify-otp")

JWT_SECRET: Optional[str] = os.getenv("GUIDORA_JWT_SECRET")
if not JWT_SECRET:
    logger.critical("Environment variable GUIDORA_JWT_SECRET is not set. Aborting startup.")
    raise RuntimeError("Missing required environment variable: GUIDORA_JWT_SECRET")

JWT_ALGORITHM = os.getenv("GUIDORA_JWT_ALGO", "HS256")
try:
    JWT_EXPIRE_DAYS = int(os.getenv("GUIDORA_JWT_EXPIRE_DAYS", "3"))
except ValueError:
    JWT_EXPIRE_DAYS = 3

class VerifyOtpRequest(BaseModel):
    number: str
    otp: str
    roll: bool = False

class VerifyOtpResponse(BaseModel):
    token: str
    uid: str

@router.post("/verify_otp", response_model=VerifyOtpResponse)
async def verify_otp_endpoint(payload: VerifyOtpRequest):
    number = payload.number.strip()
    otp = payload.otp.strip()
    roll = payload.roll

    model_cls = Specialties if roll else User
    obj = model_cls.objects(number=number).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Number not found")

    if not getattr(obj, "otp", None) or obj.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    if getattr(obj, "otp_set_at", None) and (datetime.utcnow() - obj.otp_set_at).total_seconds() > 180:
        try:
            obj.update(unset__otp=1, unset__otp_set_at=1)
        except Exception:
            logger.exception("Failed to unset expired OTP fields")
        raise HTTPException(status_code=400, detail="OTP expired")

    expire_at = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    token_payload = {
        "uid": str(obj.id),
        "number": number,
        "roll": roll,
        "exp": expire_at
    }

    try:
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception as e:
        logger.exception("Failed to encode JWT")
        raise HTTPException(status_code=500, detail="Token generation error")

    try:
        obj.token = token
        obj.save()
        obj.update(unset__otp=1, unset__otp_set_at=1)
    except Exception as e:
        logger.exception("Failed to save token to database")
        raise HTTPException(status_code=500, detail="Database error")

    return {"token": token, "uid": str(obj.id)}
