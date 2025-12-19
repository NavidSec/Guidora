from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Union
import os
import logging
from database.database import User, Specialties

log = logging.getLogger(__name__)
router = APIRouter()

class CurrentUser_info(BaseModel):
    uid: str
    token: str

class SpecialistData(BaseModel):
    uid: str
    fname: Optional[str] = ""
    lname: Optional[str] = ""
    age: Optional[int] = None
    gender: Optional[str] = ""
    number: Optional[str] = ""
    educert: Optional[str] = ""
    about: Optional[str] = ""
    tag: Optional[List[str]] = []

class UserData(BaseModel):
    uid: str
    number: str
    fname: Optional[str] = ""
    lname: Optional[str] = ""
    gender: Optional[str] = ""
    age: Optional[int] = None
    role: str

class HomeData(BaseModel):
    current_user: Union[UserData, SpecialistData]
    specialists: List[SpecialistData]

@router.post("/homepage", response_model=HomeData)
async def get_home_data(CurrentUser: CurrentUser_info):
    try:
        # جستجو با pk چون اندروید _id را می‌فرستد
        user = User.objects(pk=CurrentUser.uid).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # اصلاح: فیلد توکن در دیتابیس شما 'token' نام دارد
        if getattr(user, "token", "") != CurrentUser.token:
            raise HTTPException(status_code=401, detail="Invalid token")

        is_specialist = Specialties.objects(pk=user.id).first() is not None
        role_type = "specialist" if is_specialist else "user"

        # ساخت اطلاعات کاربر فعلی
        if role_type == "specialist":
            user_info = SpecialistData(
                uid=str(user.id),
                fname=getattr(user, "fname", ""),
                lname=getattr(user, "lname", ""),
                tag=getattr(user, "tag", []),
                about=getattr(user, "about", "")
            )
        else:
            user_info = UserData(
                uid=str(user.id),
                number=user.number,
                fname=getattr(user, "fname", ""),
                lname=getattr(user, "lname", ""),
                role=role_type
            )

        # لیست متخصصین
        all_specialists = Specialties.objects().all()
        specialist_list = [
            SpecialistData(
                uid=str(sp.id),
                fname=getattr(sp, "fname", ""),
                lname=getattr(sp, "lname", ""),
                tag=getattr(sp, "tag", []),
                about=getattr(sp, "about", "")
            ) for sp in all_specialists
        ]

        return {"current_user": user_info, "specialists": specialist_list}

    except Exception as e:
        log.exception("Home data error")
        raise HTTPException(status_code=500, detail=str(e))