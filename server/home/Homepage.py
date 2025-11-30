from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging
from mongoengine.errors import DoesNotExist, OperationError

from database.db import User, Specialties

router = APIRouter()
log = logging.getLogger("home")

class SpecialistData(BaseModel):
    uid: str
    fname: Optional[str] = ""
    lname: Optional[str] = ""
    gender: Optional[str] = ""
    age: Optional[int] = None
    tag: List[str] = []
    about: Optional[str] = ""
    educert: Optional[str] = ""

class UserData(BaseModel):
    uid: str
    number: str
    fname: Optional[str] = ""
    lname: Optional[str] = ""
    gender: Optional[str] = ""
    age: Optional[int] = None
    role: str

class HomeData(BaseModel):
    current_user: UserData
    specialists: List[SpecialistData]

@router.get("")
async def get_home_data(token: str):
    try:
        user = User.objects(token=token).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        is_specialist = Specialties.objects(uid=user.uid).first() is not None
        role_type = "specialist" if is_specialist else "user"
        
        user_info = UserData(
            uid=user.uid,
            number=user.number,
            fname=getattr(user, 'fname', ""),
            lname=getattr(user, 'lname', ""),
            gender=getattr(user, 'gender', ""),
            age=getattr(user, 'age', None),
            role=role_type
        )
        
        all_specialists = Specialties.objects().all()
        specialist_list = []
        
        for sp in all_specialists:
            spec_data = SpecialistData(
                uid=sp.uid,
                fname=getattr(sp, 'fname', ""),
                lname=getattr(sp, 'lname', ""),
                gender=getattr(sp, 'gender', ""),
                age=getattr(sp, 'age', None),
                tag=getattr(sp, 'tag', []),
                about=getattr(sp, 'about', ""),
                educert=getattr(sp, 'educert', "")
            )
            specialist_list.append(spec_data)
        
        log.info(f"Home data sent for user {user.uid}")
        return {"current_user": user_info, "specialists": specialist_list}
        
    except HTTPException:
        raise
    except Exception as e:
        log.error(f"Home data error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
