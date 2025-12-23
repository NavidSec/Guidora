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

def verify_user_globally(uid: str, token: str):
    """جستجوی کاربر در هر دو کالکشن برای تایید توکن"""
    for model in [User, Specialties]:
        u = model.objects(uid=uid).first()
        if u and u.token_value == token:
            return u
    return None

@router.post("/set_user_slot")
async def set_user_slot(data: ReservationRequest):
    current_actor = verify_user_globally(data.uid, data.token)
    if not current_actor:
        raise HTTPException(status_code=401, detail="User not found or invalid token")

    specialist = Specialties.objects(
        fname=data.fname.lower(), 
        lname=data.lname.lower()
    ).first()
    
    if not specialist:
        raise HTTPException(status_code=404, detail="Specialist target not found")

    all_requested_chunks = []
    for s in data.slots:
        chunks = generate_iso_chunks(s.day, s.start, s.end)
        all_requested_chunks.extend(chunks)

    available_set = set(specialist.available_slots)
    to_be_booked = []
    unavailable = []

    for chunk in all_requested_chunks:
        if chunk in available_set:
            to_be_booked.append(chunk)
        else:
            unavailable.append(chunk)

    if not to_be_booked:
        return {
            "status": "failed",
            "message": "None of the requested slots are available",
            "unavailable_slots": unavailable
        }

   
    specialist.update(pull_all__available_slots=to_be_booked)
    current_actor.update(push_all__appointments=to_be_booked)

    return {
        "status": "success",
        "reserved_count": len(to_be_booked),
        "reserved_slots": to_be_booked,
        "unavailable_slots": unavailable
    }