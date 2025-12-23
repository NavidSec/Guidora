from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import os
from database.database import User, Specialties
from mongoengine import connect

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)

class AuthRequest(BaseModel):
    uid: str
    token: str

def verify_token_globally(uid: str, token: str):
    for model in [User]:
        user = model.objects(uid=uid).first()
        if user and user.token_value == token:
            return user
    return None

def consolidate_slots(iso_slots: List[str]) -> List[Dict]:
    if not iso_slots:
        return []

    dts = sorted([datetime.fromisoformat(s.replace('Z', '+00:00')) for s in iso_slots])
    
    merged = []
    if not dts:
        return []

    start_time = dts[0]
    current_time = dts[0]

    for i in range(1, len(dts)):
        if dts[i] == current_time + timedelta(minutes=30):
            current_time = dts[i]
        else:
            merged.append({
                "day": start_time.strftime("%Y-%m-%d"),
                "start": start_time.strftime("%H:%M"),
                "end": (current_time + timedelta(minutes=30)).strftime("%H:%M")
            })
            start_time = dts[i]
            current_time = dts[i]

    merged.append({
        "day": start_time.strftime("%Y-%m-%d"),
        "start": start_time.strftime("%H:%M"),
        "end": (current_time + timedelta(minutes=30)).strftime("%H:%M")
    })

    return merged

@router.post("/get_reserved_slots")
async def get_user_appointments(data: AuthRequest):
    user = verify_token_globally(data.uid, data.token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid UID or Token")


    raw_slots = getattr(user, 'appointments', []) or getattr(user, 'reserved_slots', [])
    
    if not raw_slots:
        return {"uid": data.uid, "message": "No appointments found", "slots": []}

    formatted_slots = consolidate_slots(raw_slots)

    final_output = {}
    for item in formatted_slots:
        day = item["day"]
        if day not in final_output:
            final_output[day] = []
        final_output[day].append({"start": item["start"], "end": item["end"]})

    return {
        "fname": f"{user.fname}",
        "lname":f"{user.lname}",
        "slots": final_output
    }