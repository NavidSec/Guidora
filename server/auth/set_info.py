from fastapi import APIRouter, HTTPException, Request
from database.database import User, Specialties

router = APIRouter()

@router.post("/set_info")
async def set_info(request: Request):
    data = await request.json()

    uid = data.get("uid")
    fname = data.get("fname")
    lname = data.get("lname")
    tag = data.get("tag", "")

    if not uid or not fname or not lname:
        raise HTTPException(status_code=400, detail="uid, fname and lname are required")

    if tag in ["edu", "law"]:
        obj = Specialties.objects(uid=uid).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname,
                set__tag=tag
            )
        else:
            obj = Specialties(
                uid=uid,
                fname=fname,
                lname=lname,
                tag=tag
            )
            obj.save()
        role = "Specialist"
    else:
        obj = User.objects(uid=uid).first()
        if obj:
            obj.update(
                set__fname=fname,
                set__lname=lname
            )
        else:
            obj = User(
                uid=uid,
                fname=fname,
                lname=lname
            )
            obj.save()
        role = "User"

    return {"ok": True, "role": role, "uid": uid, "fname": fname, "lname": lname}
