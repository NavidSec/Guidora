from fastapi import APIRouter

router = APIRouter()

@router.get("/test-slot")
async def test_slot():
    return {"message": "User slot endpoint works!"}
