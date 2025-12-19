from fastapi import APIRouter, HTTPException, Request
from database.database import User, Specialties
from bson import ObjectId

router = APIRouter()

@router.post("/set_info")
async def set_info(request: Request):
    data = await request.json()

    token = str(data.get("token", "")).strip()
    uid = str(data.get("uid", "")).strip()
    fname = str(data.get("fname", "")).strip().lower()
    lname = str(data.get("lname", "")).strip().lower()
    number = str(data.get("number", "")).strip()
    tag = data.get("tag", [])

    if not token or not uid:
        raise HTTPException(status_code=400, detail="uid and token are required")

    if not fname or not lname or not number:
        raise HTTPException(status_code=400, detail="fname, lname and number are required")

    if not number.startswith("09") or len(number) != 11 or not number.isdigit():
        raise HTTPException(status_code=400, detail="number must start with 09 and be 11 digits")

    if isinstance(tag, str):
        tag = [tag]
    elif not isinstance(tag, (list, tuple)):
        raise HTTPException(status_code=400, detail="tag must be a string or a list of strings")

    tag = [str(t).strip().lower() for t in tag if t]


    owner = Specialties.objects(uid=uid, token=token).first() \
            or User.objects(uid=uid, token=token).first()

    if not owner:
        raise HTTPException(status_code=403, detail="Invalid uid or token")


    sp = Specialties.objects(uid=uid).first()

    if sp:
        sp.update(
            set__fname=fname,
            set__lname=lname,
            set__number=number,
            set__tag=tag,
            set__token=token
        )
    else:
        sp = Specialties(
            uid=uid,
            fname=fname,
            lname=lname,
            number=number,
            tag=tag,
            token=token
        )
        sp.save()

    sp = Specialties.objects(uid=uid).first()

    return {
        "ok": True,
        "role": "Specialist",
        "uid": sp.uid,
        "fname": sp.fname,
        "lname": sp.lname,
        "number": sp.number,
        "tag": sp.tag
    }
