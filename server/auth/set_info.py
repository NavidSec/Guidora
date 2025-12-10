from fastapi import APIRouter, HTTPException, Request
from database.database import User, Specialties
from bson import ObjectId  
router = APIRouter()

@router.post("/set_info")
async def set_info(request: Request):
    data = await request.json()

    fname = str(data.get("fname", "")).strip()
    lname = str(data.get("lname", "")).strip()
    number = str(data.get("number", "")).strip()
    tag = data.get("tag", [])

    if not fname or not lname or not number:
        raise HTTPException(
            status_code=400,
            detail="fname, lname and number are required"
        )

    if not number.startswith("09") or len(number) != 11 or not number.isdigit():
        raise HTTPException(
            status_code=400,
            detail="number must start with 09 and be 11 digits"
        )

    if isinstance(tag, str):
        tag = [tag]
    elif not isinstance(tag, (list, tuple)):
        raise HTTPException(
            status_code=400,
            detail="tag must be a string or a list of strings"
        )
    tag = [str(t).strip() for t in tag if t]

    if any(t in ["edu", "law"] for t in tag):
        obj = Specialties.objects(number=number).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname,
                set__number=number,
                set__tag=tag
            )
            uid = obj.uid
        else:
            uid = str(ObjectId())  
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
        obj = User.objects(number=number).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname,
                set__number=number
            )
            uid = obj.uid
        else:
            uid = str(ObjectId()) 
            obj = User(
                uid=uid,
                fname=fname,
                lname=lname,
                number=number
            )
            obj.save()
        role = "User"

    if role == "Specialist":
        obj = Specialties.objects(uid=uid).first()
        resp_data = {
            "ok": True,
            "role": role,
            "uid": obj.uid,
            "fname": obj.fname,
            "lname": obj.lname,
            "number": obj.number,
            "tag": obj.tag
        }
    else:
        obj = User.objects(uid=uid).first()
        resp_data = {
            "ok": True,
            "role": role,
            "uid": obj.uid,
            "fname": obj.fname,
            "lname": obj.lname,
            "number": obj.number,
            "tag": None
        }

    return resp_data
