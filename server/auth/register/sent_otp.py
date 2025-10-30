# auth/sent_otp.py
import secrets
from datetime import datetime
import re
import httpx
import logging
import os
import asyncio

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from database.db import User, Specialties

router = APIRouter()
logger = logging.getLogger("auth.sent-otp")

PHONE_RE = re.compile(r"^09\d{9}$")
SMS_API_URL = os.environ.get("SMS_API_URL", "https://sms-provider.example/send")
SMS_API_KEY = os.environ.get("SMS_API_KEY", "")

OTP_EXPIRE_SECONDS = 180

class SendOtpRequest(BaseModel):
    number: str
    roll: bool = False
    fname: str | None = None
    lname: str | None = None
    age: int | None = None

def make_otp_code(length: int = 6) -> str:
    max_val = 10 ** length
    return f"{secrets.randbelow(max_val):0{length}d}"

async def _send_sms(number: str, message: str) -> tuple[bool, str | None]:
    if not SMS_API_KEY:
        return False, "SMS_API_KEY not configured"
    payload = {"number": number, "message": message, "api_key": SMS_API_KEY}
    timeout = httpx.Timeout(10.0, read=20.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(SMS_API_URL, json=payload)
        if 200 <= resp.status_code < 300:
            return True, None
        return False, f"provider returned {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, str(e)

async def expire_otp(number: str, roll: bool, delay: int = OTP_EXPIRE_SECONDS):
    await asyncio.sleep(delay)
    model_cls = Specialties if roll else User
    obj = model_cls.objects(number=number).first()
    if obj:
        obj.otp = None
        obj.otp_set_at = None
        obj.save()
        logger.info("OTP expired for %s", number)

@router.post("/send_otp")
async def send_otp_endpoint(payload: SendOtpRequest, background_tasks: BackgroundTasks):
    number = (payload.number or "").strip()
    roll = payload.roll
    fname = payload.fname
    lname = payload.lname
    age = payload.age

    if not PHONE_RE.match(number):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Must start with 09 and be 11 digits."
        )

    otp = make_otp_code(6)
    message = f"Your verification code is: {otp}"
    model_cls = Specialties if roll else User

    try:
        obj = model_cls.objects(number=number).first()
        if obj:
            obj.otp = otp
            obj.otp_set_at = datetime.utcnow()
            if fname: obj.fname = fname
            if lname: obj.lname = lname
            if age is not None: obj.age = age
            obj.save()
        else:
            kwargs = {"number": number, "otp": otp, "otp_set_at": datetime.utcnow()}
            if fname: kwargs["fname"] = fname
            if lname: kwargs["lname"] = lname
            if age is not None: kwargs["age"] = age
            obj = model_cls(**kwargs)
            obj.save()
    except Exception as e:
        logger.exception("DB save failed")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    background_tasks.add_task(expire_otp, number, roll, OTP_EXPIRE_SECONDS)

    sms_sent, sms_error = await _send_sms(number, message)

    if sms_sent:
        return {"ok": True, "otp": otp, "roll": roll, "sms_sent": True}
    else:
        logger.warning("SMS sending failed for %s: %s", number, sms_error)
        return {"ok": True, "otp": otp, "roll": roll, "sms_sent": False, "sms_error": sms_error}
