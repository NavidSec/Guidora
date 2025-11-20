from fastapi import APIRouter, HTTPException, Request
from database.db import User, Specialties

router = APIRouter()

@router.post("/set_info")
async def set_info(request: Request):
    data = await request.json()

    uid = data.get("uid")
    number = data.get("number")
    role = data.get("role")  

    if not uid or not number or role is None:
        raise HTTPException(status_code=400, detail="uid, number and role are required")

    if role:
        obj = Specialties.objects(uid=uid).first()
        if obj:
            obj.update(
                set__number=number,
                set__fname=data.get("fname"),
                set__lname=data.get("lname"),
                set__age=data.get("age"),
                set__gender=data.get("gender"),
                set__tag=data.get("tag"),
                set__idio_secret=data.get("educert"),
                set__about=data.get("about")
            )
        else:
            obj = Specialties(
                uid=uid,
                number=number,
                fname=data.get("fname"),
                lname=data.get("lname"),
                age=data.get("age"),
                gender=data.get("gender"),
                tag=data.get("tag", []),
                idio_secret=data.get("educert"),
                about=data.get("about", "")
            )
            obj.save()
    else:
        obj = User.objects(uid=uid).first()
        if obj:
            obj.update(
                set__number=number,
                set__fname=data.get("fname"),
                set__lname=data.get("lname"),
                set__age=data.get("age"),
                set__gender=data.get("gender")
            )
        else:
            obj = User(
                uid=uid,
                number=number,
                fname=data.get("fname"),
                lname=data.get("lname"),
                age=data.get("age"),
                gender=data.get("gender")
            )
            obj.save()

    return {"ok": True, "role": "Specialist" if role else "User", "uid": uid, "number": number}
