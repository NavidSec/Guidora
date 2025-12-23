from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List
from datetime import datetime, timedelta, timezone
import os
import jwt
from mongoengine import connect
from database.database import Specialties, User

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
JWT_SECRET = os.environ.get("GUIDORA_JWT_SECRET")

if not MONGO_URI or not JWT_SECRET:
    raise RuntimeError("Environment variables MONGO_URI or GUIDORA_JWT_SECRET are not set!")

connect(host=MONGO_URI)

class SlotItem(BaseModel):
    day: str = Field(..., description="YYYY-MM-DD")
    start: str = Field(..., description="HH:MM (24h)")
    end: str = Field(..., description="HH:MM (24h)")

    @field_validator("day")
    @classmethod
    def check_day(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD")
        return v

    @field_validator("start", "end")
    @classmethod
    def check_time(cls, v):
        try:
            hh, mm = map(int, v.split(":"))
            if not (0 <= hh <= 23 and 0 <= mm <= 59):
                raise ValueError()
        except Exception:
            raise ValueError("Time must be in HH:MM format (00:00-23:59)")
        return v

class AvailabilityRequest(BaseModel):
    uid: str
    token: str
    slots: List[SlotItem]

def verify_jwt_and_uid(token: str, request_uid: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        token_uid = payload.get("uid")
        if not token_uid or token_uid != request_uid:
            raise HTTPException(status_code=401, detail="Token UID mismatch. Access denied.")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="JWT token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid JWT token")

@router.post("/set_spe_avi_slots")
async def set_availability(data: AvailabilityRequest):
    req_uid = data.uid.strip().lower()
    verify_jwt_and_uid(data.token, req_uid)
    counselor = Specialties.objects(uid=req_uid).first()
    
    if not counselor:
        user_exists = User.objects(uid=req_uid).first()
        if user_exists:
            raise HTTPException(status_code=403, detail="Only specialists can set availability slots.")
        raise HTTPException(status_code=404, detail="Specialist not found in database.")

    new_slots_iso = []
    for s in data.slots:
        day_dt = datetime.strptime(s.day, "%Y-%m-%d")
        sh, sm = map(int, s.start.split(":"))
        eh, em = map(int, s.end.split(":"))
        start_dt = datetime(day_dt.year, day_dt.month, day_dt.day, sh, sm, tzinfo=timezone.utc)
        end_dt = datetime(day_dt.year, day_dt.month, day_dt.day, eh, em, tzinfo=timezone.utc)
        
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail=f"End time must be after start time for {s.day}")

        current_time = start_dt
        while current_time < end_dt:
            iso_string = current_time.isoformat().replace("+00:00", "Z")
            new_slots_iso.append(iso_string)
            current_time += timedelta(minutes=30)

    unique_slots = list(dict.fromkeys(new_slots_iso))
    try:
        counselor.available_slots = unique_slots
        counselor.save()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    return {
        "status": "success",
        "specialist": f"{counselor.fname} {counselor.lname}",
        "total_slots": len(unique_slots)
    }