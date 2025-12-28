from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mongoengine import connect, DoesNotExist
from typing import List # اضافه شد
import os
from database.database import User, Specialties

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)

class UserUpdate(BaseModel):
    uid: str
    fname: str
    lname: str
    age: int
    gender: str
    number: str
    token: str
    tag: List[str] # تغییر کرد به لیست از رشته ها

def verify_token(uid: str, token: str) -> bool:
    try:
        user = User.objects.get(uid=uid)
        return user.token_value == token
    except DoesNotExist:
        return False

@router.post("/set_user_profile")
async def update_user(data: UserUpdate):
    if not verify_token(data.uid, data.token):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid token")

    result = {}
    
    # User Model
    try:
        u_obj = User.objects.get(uid=data.uid)
        u_obj.fname = data.fname
        u_obj.lname = data.lname
        u_obj.age = data.age
        u_obj.gender = data.gender
        u_obj.number = data.number
        u_obj.save()
        result["users"] = "updated"
    except DoesNotExist:
        u_obj = User(
            uid=data.uid, fname=data.fname, lname=data.lname,
            age=data.age, gender=data.gender, number=data.number
        )
        u_obj.save()
        result["users"] = "created"

    # Specialties Model
    try:
        s_obj = Specialties.objects.get(uid=data.uid)
        s_obj.fname = data.fname
        s_obj.lname = data.lname
        s_obj.age = data.age
        s_obj.gender = data.gender
        s_obj.number = data.number
        s_obj.tag = data.tag # Pydantic به صورت خودکار لیست را مدیریت می کند
        s_obj.save()
        result["specialties"] = "updated"
    except DoesNotExist:
        s_obj = Specialties(
            uid=data.uid, fname=data.fname, lname=data.lname,
            age=data.age, gender=data.gender, number=data.number,
            tag=data.tag
        )
        s_obj.save()
        result["specialties"] = "created"

    return {"details": result}