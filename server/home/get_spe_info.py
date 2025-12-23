from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from mongoengine import connect, DoesNotExist
import os
import json
from database.database import User, Specialties

router = APIRouter()

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)

class SpecialistSearchRequest(BaseModel):
    uid: str
    jwt: str
    fname: str
    lname: str

def verify_token_globally(uid: str, token: str) -> bool:

    for model in [User, Specialties]:
        try:
            target_user = model.objects.get(uid=uid)
            if hasattr(target_user, 'token_value') and target_user.token_value == token:
                return True
        except DoesNotExist:
            continue
    return False

@router.post("/get_spe_info")
async def get_specialist_info(data: SpecialistSearchRequest):
    if not verify_token_globally(data.uid, data.jwt):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid token or UID not found")

    try:
        specialist = Specialties.objects.get(fname=data.fname, lname=data.lname)
        
        specialist_data = specialist.to_mongo().to_dict()
        
        if "_id" in specialist_data:
            specialist_data["_id"] = str(specialist_data["_id"])

        return specialist_data

    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Specialist with these names not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")