from fastapi import APIRouter

router = APIRouter()

@router.get("/list")
async def list_users():
    return {"users": ["Alice", "Bob"]}
