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

class BookingSlot(BaseModel):
    day: str    
    start: str  
    end: str    

class ReservationRequest(BaseModel):
    uid: str
    token: str
    fname: str
    lname: str
    slots: List[BookingSlot]

def generate_iso_chunks(day_str, start_str, end_str):
    day = datetime.strptime(day_str, "%Y-%m-%d")
    sh, sm = map(int, start_str.split(":"))
    eh, em = map(int, end_str.split(":"))
    
    start_dt = datetime(day.year, day.month, day.day, sh, sm, tzinfo=timezone.utc)
    end_dt = datetime(day.year, day.month, day.day, eh, em, tzinfo=timezone.utc)
    
    chunks = []
    cur = start_dt
    while cur < end_dt:
        iso = cur.isoformat().replace("+00:00", "Z")
        chunks.append(iso)
        cur += timedelta(minutes=30)
    return chunks

@router.post("/set_user_slot")
async def set_user_slot(data: ReservationRequest):
    current_user = User.objects(uid=data.uid).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if current_user.token_value != data.token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    specialist = Specialties.objects(
        fname=data.fname.lower(), 
        lname=data.lname.lower()
    ).first()
    
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")

    successful_bookings = []
    unavailable_slots = []

    for s in data.slots:
        requested_chunks = generate_iso_chunks(s.day, s.start, s.end)
        
        for chunk in requested_chunks:
            if chunk in specialist.available_slots:
                specialist.update(pull__available_slots=chunk)
                successful_bookings.append(chunk)
            else:
                unavailable_slots.append(chunk)

    if successful_bookings:
        current_user.update(push_all__appointments=successful_bookings)

    return {
        "status": "success" if successful_bookings else "failed",
        "reserved_count": len(successful_bookings),
        "reserved_slots": successful_bookings,
        "unavailable_slots": unavailable_slots,
        "message": f"Successfully reserved {len(successful_bookings)} slots."
    }