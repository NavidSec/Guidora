from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from mongoengine import connect, DoesNotExist
import os
from allusers import User, Specialties  

MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)

app = FastAPI()

class UserUpdate(BaseModel):
    uid: str
    fname: str
    lname: str
    age: int
    gender: str
    number:int
    token: str

def verify_token(uid: str, token: str) -> bool:
    try:
        user = User.objects.get(uid=uid)
        return user.token_value == token
    except DoesNotExist:
        return False

@app.post("/set_user_profile")
async def update_user(data: UserUpdate):
    if not verify_token(data.uid, data.token):
        raise HTTPException(status_code=401, detail="Unauthorized: invalid token")

    result = {}
    for model, name in [(User, "users"), (Specialties, "specialties")]:
        try:
            obj = model.objects.get(uid=data.uid)
            obj.fname = data.fname
            obj.lname = data.lname
            obj.age = data.age
            obj.gender = data.gender
            number=data.number 
            obj.save()
            result[name] = "updated"
        except DoesNotExist:
            obj = model(
                uid=data.uid,
                fname=data.fname,
                lname=data.lname,
                age=data.age,
                gender=data.gender,
                number=data.number 
            )
            obj.save()
            result[name] = "created"

    return {"status": "success", "details": result}
