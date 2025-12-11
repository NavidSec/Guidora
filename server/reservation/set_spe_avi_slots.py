from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List
from datetime import datetime, timedelta, timezone
import os
import jwt  # PyJWT
from mongoengine import connect
from database.database import Specialties  

MONGO_URI = os.environ.get("MONGO_URI")
JWT_SECRET = os.environ.get("GUIDORA_JWT_SECRET")
if not MONGO_URI or not JWT_SECRET:
    raise RuntimeError("Environment variables MONGO_URI or GUIDORA_JWT_SECRET are not set!")

connect(host=MONGO_URI)

router = APIRouter()

class SlotItem(BaseModel):
    day: str = Field(..., description="YYYY-MM-DD")
    start: str = Field(..., description="HH:MM (24h)")
    end: str = Field(..., description="HH:MM (24h)")

    @validator("day")
    def check_day(cls, v):
        datetime.strptime(v, "%Y-%m-%d")
        return v

    @validator("start", "end")
    def check_time(cls, v):
        hh, mm = map(int, v.split(":"))
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError("time out of range")
        return v

class AvailabilityRequest(BaseModel):
    uid: str
    token: str
    slots: List[SlotItem]

def decode_and_verify_jwt(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

@router.post("/set_spe_avi_slots")
def set_availability(data: AvailabilityRequest):
    req_uid = data.uid.strip().lower()
    counselor = Specialties.objects(uid=req_uid).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    if not data.token:
        raise HTTPException(status_code=401, detail="token is required in body")

    decode_and_verify_jwt(data.token)  
    new_slots_iso = []
    for s in data.slots:
        day = datetime.strptime(s.day, "%Y-%m-%d")
        sh, sm = map(int, s.start.split(":"))
        eh, em = map(int, s.end.split(":"))
        start_dt = datetime(day.year, day.month, day.day, sh, sm, tzinfo=timezone.utc)
        end_dt = datetime(day.year, day.month, day.day, eh, em, tzinfo=timezone.utc)
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail=f"end must be after start for {s.day}")

        cur = start_dt
        while cur < end_dt:
            iso = cur.isoformat().replace("+00:00", "Z")
            new_slots_iso.append(iso)
            cur += timedelta(minutes=30)

    unique_slots = list(dict.fromkeys(new_slots_iso))  

    try:
        counselor.available_slots = unique_slots
        counselor.save()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save slots to database")

    return {"message": f"{len(unique_slots)} time slots stored"}
