from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timedelta
import os
import jwt
from mongoengine import connect
from database.database import Specialties

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
JWT_SECRET = os.environ.get("GUIDORA_JWT_SECRET")

if not MONGO_URI or not JWT_SECRET:
    raise RuntimeError("Environment variables are not set!")

connect(host=MONGO_URI)

class SlotItem(BaseModel):
    day: str
    start: str
    end: str

class AvailabilityRequest(BaseModel):
    uid: str
    token: str
    slots: List[SlotItem]

def verify_jwt_and_uid(token: str, request_uid: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if str(payload.get("uid")) != str(request_uid):
            return False
        return True
    except:
        return False

@router.post("/set_spe_avi_slots")
async def set_availability(data: AvailabilityRequest):
    # ۱. تایید هویت
    clean_uid = data.uid.strip()
    if not verify_jwt_and_uid(data.token, clean_uid):
        raise HTTPException(status_code=401, detail="Authentication failed")

    # ۲. پیدا کردن مشاور
    specialist = Specialties.objects(uid=clean_uid).first()
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    # ۳. تولید اسلات‌ها
    generated_chunks = []
    for s in data.slots:
        try:
            # پارس کردن تاریخ و زمان (بدون درگیری با Timezone برای سادگی)
            day_parts = list(map(int, s.day.split("-")))
            sh, sm = map(int, s.start.split(":"))
            eh, em = map(int, s.end.split(":"))

            start_dt = datetime(day_parts[0], day_parts[1], day_parts[2], sh, sm)
            end_dt = datetime(day_parts[0], day_parts[1], day_parts[2], eh, em)

            curr = start_dt
            while curr < end_dt:
                # فرمت: 2025-12-28T08:00Z
                iso_string = curr.strftime("%Y-%m-%dT%H:%MZ")
                generated_chunks.append(iso_string)
                curr += timedelta(minutes=30)
        except Exception as e:
            print(f"Error processing slot item: {e}")
            continue

    if not generated_chunks:
        raise HTTPException(status_code=400, detail="Could not generate any time slots")

    # ۴. ذخیره در دیتابیس
    unique_chunks = list(dict.fromkeys(generated_chunks))
    try:
        # پاکسازی اسلات‌های قبلی و جایگزینی با جدید
        specialist.update(set__available_slots=unique_chunks)
        return {"status": "success", "count": len(unique_chunks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")