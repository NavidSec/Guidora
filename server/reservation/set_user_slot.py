from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime, timedelta
import os
import jwt
from database.database import User, Specialties
from mongoengine import connect

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
JWT_SECRET = os.environ.get("GUIDORA_JWT_SECRET")

if not MONGO_URI or not JWT_SECRET:
    raise RuntimeError("Environment variables are not set!")

connect(host=MONGO_URI)

class AuthRequest(BaseModel):
    uid: str
    token: str

def verify_jwt_and_uid(token: str, request_uid: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        token_uid = payload.get("uid")
        if not token_uid or token_uid != request_uid:
            raise HTTPException(status_code=401, detail="Token UID mismatch")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

def consolidate_slots(iso_slots: List[str]) -> List[Dict]:
    if not iso_slots:
        return []

    dts = sorted([datetime.fromisoformat(s.replace('Z', '+00:00')) for s in iso_slots])
    merged = []
    if not dts: return []

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
    verify_jwt_and_uid(data.token, data.uid)

    user = User.objects(uid=data.uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    raw_slots = user.appointments
    if not raw_slots:
        return {
            "fname": user.fname,
            "lname": user.lname,
            "specialist": None,
            "slots": {}
        }
    
    formatted_slots = consolidate_slots(raw_slots)
    
    final_output = {}
    for item in formatted_slots:
        day = item["day"]
        if day not in final_output:
            final_output[day] = []
        final_output[day].append({"start": item["start"], "end": item["end"]})

    return {
        "fname": user.fname,
        "lname": user.lname,
        "slots": final_output
    }