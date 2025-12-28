from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
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


class CancelReservationRequest(BaseModel):
    uid: str
    token: str
    fname: str
    lname: str


def verify_jwt_and_uid(token: str, request_uid: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        token_uid = payload.get("uid")
        if not token_uid or token_uid != request_uid:
            raise HTTPException(status_code=401, detail="Token UID mismatch")
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/del_reserved_slots")
async def del_reserved_slots(data: CancelReservationRequest):
    verify_jwt_and_uid(data.token, data.uid)

    user = User.objects(uid=data.uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.appointments or len(user.appointments) == 0:
        raise HTTPException(status_code=400, detail="No reservations to cancel")

    if (getattr(user, "reserved_specialist_fname", "").lower() != data.fname.lower() or
        getattr(user, "reserved_specialist_lname", "").lower() != data.lname.lower()):
        raise HTTPException(status_code=400, detail="This reservation is not with the specified specialist")

    try:
        user.update(
            unset__appointments=1,
            unset__last_specialist_uid=1,
            unset__reserved_specialist_fname=1,
            unset__reserved_specialist_lname=1,
            unset__reserved_specialist_number=1
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to cancel reservation")

    return {"status": "success", "message": "Reservation cancelled successfully"}
