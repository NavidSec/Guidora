from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from mongoengine import connect, DoesNotExist
import os
from database.database import Specialties

router = APIRouter()  

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)

class SpecialtiesUpdate(BaseModel):
    uid: str
    fname: str
    lname: str
    age: int
    gender: str
    token: str
    number: str
    educert: Optional[str] = ""
    about: Optional[str] = ""
    tag: Optional[str] = ""  

def verify_token(uid: str, token: str) -> bool:
    try:
        user = Specialties.objects.get(uid=uid)
        return user.token_value == token
    except DoesNotExist:
        return False

@router.post("/set_spe_profile") 
async def update_specialist(data: SpecialtiesUpdate):
    if not verify_token(data.uid, data.token):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid token")

    tag_upper = data.tag.upper()
    if tag_upper not in {"LAW", "EDU"}:
        raise HTTPException(status_code=400, detail="Invalid tag value, must be 'law' or 'edu'")

    try:
        specialist = Specialties.objects.get(uid=data.uid)
        specialist.fname = data.fname
        specialist.lname = data.lname
        specialist.age = data.age
        specialist.gender = data.gender
        specialist.number = data.number
        specialist.educert = data.educert
        specialist.about = data.about
        specialist.tag = [tag_upper]
        specialist.save()
        status = "updated"
    except DoesNotExist:
        specialist = Specialties(
            uid=data.uid,
            fname=data.fname,
            lname=data.lname,
            age=data.age,
            gender=data.gender,
            number=data.number,
            token=data.token,
            educert=data.educert,
            about=data.about,
            tag=[tag_upper]
        )
        specialist.save()
        status = "created"

    return {"status": status}
