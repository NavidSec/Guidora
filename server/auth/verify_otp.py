import os
from datetime import datetime, timedelta
import logging
import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.database import User

router = APIRouter()
logger = logging.getLogger("auth.verify_otp")

# تنظیمات JWT
JWT_SECRET = os.getenv("GUIDORA_JWT_SECRET", "your-fallback-secret")
JWT_ALGORITHM = os.getenv("GUIDORA_JWT_ALGO", "HS256")

try:
    JWT_EXPIRE_DAYS = int(os.getenv("GUIDORA_JWT_EXPIRE_DAYS", "3"))
except ValueError:
    JWT_EXPIRE_DAYS = 3

class VerifyOtpRequest(BaseModel):
    number: str
    otp: str

class VerifyOtpResponse(BaseModel):
    token: str
    uid: str

@router.post("/verify_otp", response_model=VerifyOtpResponse)
async def verify_otp_endpoint(payload: VerifyOtpRequest):
    number = payload.number.strip()
    otp = payload.otp.strip()

    obj = User.objects(number=number).first()

    if not obj:
        raise HTTPException(status_code=404, detail="شماره موبایل یافت نشد")

    if not getattr(obj, "otp", None) or obj.otp != otp:
        raise HTTPException(status_code=400, detail="کد وارد شده اشتباه است")

    if getattr(obj, "otp_set_at", None):
        diff = (datetime.utcnow() - obj.otp_set_at).total_seconds()
        if diff > 180:
            obj.update(unset__otp=1, unset__otp_set_at=1)
            raise HTTPException(status_code=400, detail="کد منقضی شده است")

    user_uid = str(obj.uid) 

    expire_at = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    
    token_payload = {
        "uid": user_uid,
        "number": number,
        "exp": expire_at
    }

    try:
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception as e:
        logger.exception("Failed to encode JWT")
        raise HTTPException(status_code=500, detail="خطا در تولید توکن")

    try:
        obj.update(
            set__token=token,
            unset__otp=1,
            unset__otp_set_at=1
        )
    except Exception as e:
        logger.exception("Failed to save token to database")
        raise HTTPException(status_code=500, detail="خطای دیتابیس در ذخیره توکن")

    return {"token": token, "uid": user_uid}