from fastapi import FastAPI, HTTPException
from models import Specialties, TimeSlot
from mongoengine import connect
from datetime import datetime, timedelta
from pydantic import BaseModel
from datetime import datetime
from typing import List


MONGO_URI = os.environ.get("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set!")

connect(host=MONGO_URI)
app = FastAPI()

class AvailabilityRequest(BaseModel):
    uid: str
    slots: List[dict]   

@app.post("/set_spe_avi_slots")
def set_availability(data: AvailabilityRequest):
    counselor = Specialties.objects(uid=data.uid).first()
    if not counselor:
        raise HTTPException(status_code=404, detail="Counselor not found")

    new_slots = []

    for slot in data.slots:
        day_str = slot['day']  
        start_str = slot['start']  
        end_str = slot['end']      

        day = datetime.strptime(day_str, "%Y-%m-%d")
        start_hour, start_min = map(int, start_str.split(":"))
        end_hour, end_min = map(int, end_str.split(":"))

        slot_start = day.replace(hour=start_hour, minute=start_min)
        slot_end = day.replace(hour=end_hour, minute=end_min)

        current = slot_start
        while current < slot_end:
            next_slot = current + timedelta(minutes=30)
            new_slots.append(TimeSlot(start=current, end=next_slot))
            current = next_slot

    counselor.available_slots = new_slots  
    counselor.save()

    return {"message": f"{len(new_slots)} time slots stored for counselor {counselor.fname} {counselor.lname}"}
