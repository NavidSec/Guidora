import secrets
from datetime import datetime
import re
import httpx
import logging
import os
import asyncio
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from database.db import User

router = APIRouter()
logger = logging.getLogger("auth.sent_otp")

PHONE_RE = re.compile(r"^09\d{9}$")
SMS_API_URL = os.environ.get("SMS_API_URL", "https://sms-provider.example/send")
SMS_API_KEY = os.environ.get("SMS_API_KEY", "")

OTP_EXPIRE_SECONDS = 180

def generate_uid() -> str:
    return uuid.uuid4().hex

class SendOtpRequest(BaseModel):
    number: str

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

async def expire_otp(number: str, delay: int = OTP_EXPIRE_SECONDS):
    await asyncio.sleep(delay)
    obj = User.objects(number=number).first()
    if obj:
        obj.otp = None
        obj.otp_set_at = None
        obj.save()
        logger.info("OTP expired for %s", number)

@router.post("/send_otp")
async def send_otp_endpoint(payload: SendOtpRequest, background_tasks: BackgroundTasks):
    number = (payload.number or "").strip()

    if not PHONE_RE.match(number):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Must start with 09 and be 11 digits."
        )

    otp = make_otp_code(6)
    message = f"Your verification code is: {otp}"

    try:
        now = datetime.utcnow()
        result = User.objects(number=number).update_one(
            upsert=True,
            set__otp=otp,
            set__otp_set_at=now,
            set__number=number,
            set_on_insert__uid=generate_uid(),
            set_on_insert__created_at=now
        )
        logger.info("OTP stored/updated for %s (update result: %s)", number, result)
    except Exception as e:
        logger.exception("Database upsert failed for number=%s", number)
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

    background_tasks.add_task(expire_otp, number, OTP_EXPIRE_SECONDS)

    sms_sent, sms_error = await _send_sms(number, message)

    if sms_sent:
        return {"ok": True, "sms_sent": True}
    else:
        logger.warning("SMS sending failed for %s: %s", number, sms_error)
        return {"ok": True, "sms_sent": False, "sms_error": sms_error}
