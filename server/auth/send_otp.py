import re
import httpx
import logging
import os
import asyncio
import uuid

from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel

from database.database import User


router = APIRouter()
logger = logging.getLogger("auth.send_otp")

PHONE_RE = re.compile(r"^09\d{9}$")

SMS_API_URL = os.environ.get(
    "SMS_API_URL"
)

OTP_EXPIRE_SECONDS = 180


def generate_uid() -> str:
    return uuid.uuid4().hex


class SendOtpRequest(BaseModel):
    number: str


async def send_otp_via_provider(number: str) -> tuple[bool, str | None, str | None]:
    """
    Melipayamak generates OTP.
    We only receive it and store it.
    """
    payload = {"to": number}
    timeout = httpx.Timeout(10.0, read=20.0)

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(SMS_API_URL, json=payload)

        if resp.status_code != 200:
            return False, None, f"HTTP {resp.status_code}"

        data = resp.json()
        logger.info("Melipayamak response: %s", data)

        status = str(data.get("status", "")).lower()
        otp_code = data.get("code")

        success_keywords = ["موفق", "success", "sent"]

        if any(k in status for k in success_keywords) and otp_code:
            return True, otp_code, None

        return False, None, f"Provider error: {data}"

    except Exception as e:
        logger.exception("SMS provider error")
        return False, None, str(e)


async def expire_otp(number: str, delay: int):
    await asyncio.sleep(delay)

    user = User.objects(number=number).first()
    if user and user.otp_set_at:
        user.otp = None
        user.otp_set_at = None
        user.save()
        logger.info("OTP expired for %s", number)


@router.post("/send_otp")
async def send_otp_endpoint(
    payload: SendOtpRequest,
    background_tasks: BackgroundTasks
):
    number = payload.number.strip()

    if not PHONE_RE.match(number):
        raise HTTPException(status_code=400, detail="Invalid phone number")

    success, otp_code, error = await send_otp_via_provider(number)

    if not success:
        raise HTTPException(status_code=502, detail="SMS provider failed")

    now = datetime.utcnow()

    try:
        User.objects(number=number).update_one(
            upsert=True,
            set__number=number,
            set__otp=otp_code,
            set__otp_set_at=now,
            set_on_insert__uid=generate_uid(),
            set_on_insert__created_at=now
        )
    except Exception:
        logger.exception("Database error")
        raise HTTPException(status_code=500, detail="Database error")

    background_tasks.add_task(expire_otp, number, OTP_EXPIRE_SECONDS)

    return {
        "ok": True,
        "sms_sent": True
    }
