from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

from database.db import User, Specialties

router = APIRouter()
logger = logging.getLogger("home")

class SpecialistInfo(BaseModel):
    uid: str
    fname: Optional[str] = None
    lname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    tag: List[str] = []
    about: Optional[str] = None
    educert: Optional[str] = None

class UserInfo(BaseModel):
    uid: str
    number: str
    fname: Optional[str] = None
    lname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    role: str

class HomeResponse(BaseModel):
    current_user: UserInfo
    specialists: List[SpecialistInfo]

@router.get("/home")
async def get_homepage(token: str):
    user = User.objects(token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    specialist_check = Specialties.objects(uid=user.uid).first()
    user_role = "specialist" if specialist_check else "user"
    
    user_data = UserInfo(
        uid=user.uid,
        number=user.number,
        fname=user.fname,
        lname=user.lname,
        gender=user.gender,
        age=user.age,
        role=user_role
    )
    
    all_specialists = Specialties.objects().all()
    specialists_list = []
    
    for spec in all_specialists:
        spec_info = SpecialistInfo(
            uid=spec.uid,
            fname=spec.fname,
            lname=spec.lname,
            gender=spec.gender,
            age=spec.age,
            tag=spec.tag if hasattr(spec, 'tag') else [],
            about=spec.about if hasattr(spec, 'about') else "",
            educert=spec.educert if hasattr(spec, 'educert') else ""
        )
        specialists_list.append(spec_info)
    
    logger.info(f"Homepage data sent for user {user.uid}. Specialists count: {len(specialists_list)}")
    
    return HomeResponse(
        current_user=user_data,
        specialists=specialists_list
    )
