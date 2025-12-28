from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
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
    raise RuntimeError("Environment variables are not set!")

connect(host=MONGO_URI)

class BookingSlot(BaseModel):
    day: str = Field(..., description="YYYY-MM-DD")
    start: str = Field(..., description="HH:MM")
    end: str = Field(..., description="HH:MM")

class ReservationRequest(BaseModel):
    uid: str
    token: str
    fname: str
    lname: str
    slots: List[BookingSlot]

def verify_jwt_and_uid(token: str, request_uid: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        token_uid = payload.get("uid")
        if not token_uid or token_uid != request_uid:
            raise HTTPException(status_code=401, detail="Token UID mismatch")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def generate_iso_chunks(day_str, start_str, end_str):
    day = datetime.strptime(day_str, "%Y-%m-%d")
    sh, sm = map(int, start_str.split(":"))
    eh, em = map(int, end_str.split(":"))
    start_dt = datetime(day.year, day.month, day.day, sh, sm, tzinfo=timezone.utc)
    end_dt = datetime(day.year, day.month, day.day, eh, em, tzinfo=timezone.utc)
    chunks = []
    cur = start_dt
    while cur < end_dt:
        iso = cur.strftime("%Y-%m-%dT%H:%MZ") 
        chunks.append(iso)
        cur += timedelta(minutes=30)
    return chunks

@router.post("/set_user_slot")
async def set_user_slot(data: ReservationRequest):
    verify_jwt_and_uid(data.token, data.uid)
    current_user = User.objects(uid=data.uid).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    specialist = Specialties.objects(
        fname=data.fname.lower(), 
        lname=data.lname.lower()
    ).first()
    
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    all_requested_chunks = []
    try:
        for s in data.slots:
            chunks = generate_iso_chunks(s.day, s.start, s.end)
            all_requested_chunks.extend(chunks)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid date or time format")

    available_set = set(specialist.available_slots)
    to_be_booked = [chunk for chunk in all_requested_chunks if chunk in available_set]

    if not to_be_booked or len(to_be_booked) != len(all_requested_chunks):
        raise HTTPException(status_code=400, detail="این زمان رزرو شده!  زمان دیگری را انتخاب کنید")

    try:
        specialist.update(pull_all__available_slots=to_be_booked)

        current_user.update(
            set__appointments=to_be_booked,
            set__last_specialist_uid=specialist.uid,
            set__reserved_specialist_fname=specialist.fname,
            set__reserved_specialist_lname=specialist.lname,
            set__reserved_specialist_number=specialist.number
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Database update failed")

    return {"status": "success", "reserved_count": len(to_be_booked)}