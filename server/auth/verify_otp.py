import os
from datetime import datetime, timedelta
import logging

import jwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database.database import User, Specialties

router = APIRouter()
logger = logging.getLogger("auth.verify_otp")

JWT_SECRET: str = os.getenv("GUIDORA_JWT_SECRET")
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

    # پیدا کردن کاربر بر اساس شماره موبایل
    obj = User.objects(number=number).first()

    if not obj:
        raise HTTPException(status_code=404, detail="Number not found")

    # بررسی صحت OTP
    if not getattr(obj, "otp", None) or obj.otp != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # بررسی انقضای OTP (۳ دقیقه)
    if getattr(obj, "otp_set_at", None) and (datetime.utcnow() - obj.otp_set_at).total_seconds() > 180:
        try:
            obj.update(unset__otp=1, unset__otp_set_at=1)
        except Exception:
            logger.exception("Failed to unset expired OTP fields")
        raise HTTPException(status_code=400, detail="OTP expired")

    # تولید توکن JWT
    expire_at = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    
    # استفاده از str(obj.id) به عنوان UID اصلی (مطابق با _id در مونگو)
    user_id_str = str(obj.id)
    
    token_payload = {
        "uid": user_id_str,
        "number": number,
        "exp": expire_at
    }

    try:
        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    except Exception as e:
        logger.exception("Failed to encode JWT")
        raise HTTPException(status_code=500, detail="Token generation error")

    try:
        # ذخیره توکن در دیتابیس
        # نکته: اگر می‌خواهید فیلد uid دیتابیس هم با id مونگو یکی شود، خط زیر را اضافه کنید:
        # obj.uid = user_id_str 
        
        obj.token = token
        obj.save()
        
        # پاک کردن OTP بعد از ورود موفق
        obj.update(unset__otp=1, unset__otp_set_at=1)
    except Exception as e:
        logger.exception("Failed to save token to database")
        raise HTTPException(status_code=500, detail="Database error")

    # برگرداندن همان مقداری که در توکن و دیتابیس (به عنوان _id) وجود دارد
    return {"token": token, "uid": user_id_str}