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
        # --- اصلاح اصلی اینجاست ---
        # به جای pk از فیلد uid استفاده می‌کنیم تا با رشته 32 کاراکتری سازگار باشد
        user = User.objects(uid=CurrentUser.uid).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if getattr(user, "token", "") != CurrentUser.token:
            raise HTTPException(status_code=401, detail="Invalid token")

        # بررسی وجود در جدول متخصصین بر اساس uid اختصاصی
        specialist_record = Specialties.objects(uid=user.uid).first()
        is_specialist = specialist_record is not None
        role_type = "specialist" if is_specialist else "user"

        if role_type == "specialist":
            # استفاده از user.uid به جای user.id برای جلوگیری از خطای ObjectId
            user_info = SpecialistData(
                uid=str(user.uid), 
                fname=getattr(user, "fname", ""),
                lname=getattr(user, "lname", ""),
                tag=getattr(user, "tag", []),
                about=getattr(user, "about", "")
            )
        else:
            user_info = UserData(
                uid=str(user.uid),
                number=user.number,
                fname=getattr(user, "fname", ""),
                lname=getattr(user, "lname", ""),
                role=role_type
            )

        # دریافت لیست تمام متخصصین
        all_specialists = Specialties.objects().all()
        specialist_list = [
            SpecialistData(
                uid=str(sp.uid), # اینجا هم از uid استفاده کنید
                fname=getattr(sp, "fname", ""),
                lname=getattr(sp, "lname", ""),
                tag=getattr(sp, "tag", []),
                about=getattr(sp, "about", "")
            ) for sp in all_specialists
        ]

        return {"current_user": user_info, "specialists": specialist_list}

    except HTTPException as he:
        # خطاهای HTTP (مثل 401 و 404) را دوباره پرتاب می‌کنیم
        raise he
    except Exception as e:
        log.exception("Home data error")
        # جلوگیری از نمایش جزئیات فنی خطا به کاربر برای امنیت بیشتر
        raise HTTPException(status_code=500, detail="Internal Server Error")