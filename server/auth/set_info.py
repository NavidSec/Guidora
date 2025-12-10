from fastapi import APIRouter, HTTPException, Request
from database.database import User, Specialties

router = APIRouter()

@router.post("/set_info")
async def set_info(request: Request):
    data = await request.json()

    uid = data.get("uid")
    fname = data.get("fname")
    lname = data.get("lname")
    number = data.get("number")
    tag = data.get("tag", "")

    # اعتبارسنجی اولیه
    if not uid or not fname or not lname or not number:
        raise HTTPException(
            status_code=400, 
            detail="uid, fname, lname and number are required"
        )

    if not isinstance(number, str) or not number.startswith("09") or len(number) != 11:
        raise HTTPException(
            status_code=400,
            detail="number must start with 09 and be 11 digits"
        )

    # مدیریت Specialties
    if tag in ["edu", "law"]:
        obj = Specialties.objects(uid=uid).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname,
                set__tag=tag,
                set__number=number
            )
        else:
            obj = Specialties(
                uid=uid,
                fname=fname,
                lname=lname,
                number=number,
                tag=tag
            )
            obj.save()
        role = "Specialist"
    else:
        # مدیریت User
        obj = User.objects(uid=uid).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname,
                set__number=number
            )
        else:
            obj = User(
                uid=uid,
                fname=fname,
                lname=lname,
                number=number
            )
            obj.save()
        role = "User"

    return {
        "ok": True,
        "role": role,
        "uid": uid,
        "fname": fname,
        "lname": lname,
        "number": number
    }
