from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging

from database.db import User, Specialties

router = APIRouter()
logger = logging.getLogger("home")

class SpecialistInfo(BaseModel):
    uid: str
    fname: Optional[str] = None
    lname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    tag: List[str] = []
    about: Optional[str] = None
    educert: Optional[str] = None

class UserInfo(BaseModel):
    uid: str
    number: str
    fname: Optional[str] = None
    lname: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    role: str  # "user" or "specialist"

class HomeResponse(BaseModel):
    current_user: UserInfo
    specialists: List[SpecialistInfo]

def get_current_user(token: str) -> User:
    """Extract and validate current user from token"""
    user = User.objects(token=token).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@router.get("/home", response_model=HomeResponse)
async def get_homepage(token: str):
    """
    Get homepage data including current user info and all specialists
    """
    try:
        # Get current user
        current_user = get_current_user(token)
        
        # Determine user role and prepare user info
        is_specialist = Specialties.objects(uid=current_user.uid).first() is not None
        role = "specialist" if is_specialist else "user"
        
        user_info = UserInfo(
            uid=current_user.uid,
            number=current_user.number,
            fname=current_user.fname,
            lname=current_user.lname,
            gender=current_user.gender,
            age=current_user.age,
            role=role
        )
        
        # Get all specialists with their complete information
        specialists_data = []
        specialists = Specialties.objects().all()
        
        for specialist in specialists:
            specialist_info = SpecialistInfo(
                uid=specialist.uid,
                fname=specialist.fname,
                lname=specialist.lname,
                gender=specialist.gender,
                age=specialist.age,
                tag=specialist.tag if hasattr(specialist, 'tag') else [],
                about=specialist.about if hasattr(specialist, 'about') else "",
                educert=specialist.educert if hasattr(specialist, 'educert') else ""
            )
            specialists_data.append(specialist_info)
        
        logger.info(f"Homepage data retrieved for user {current_user.uid}. Found {len(specialists_data)} specialists.")
        
        return HomeResponse(
            current_user=user_info,
            specialists=specialists_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error retrieving homepage data: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Optional: Add a public endpoint to get only specialists (if needed for non-authenticated views)
@router.get("/public/specialists", response_model=List[SpecialistInfo])
async def get_public_specialists():
    """
    Get all specialists (public endpoint without authentication)
    """
    try:
        specialists_data = []
        specialists = Specialties.objects().all()
        
        for specialist in specialists:
            specialist_info = SpecialistInfo(
                uid=specialist.uid,
                fname=specialist.fname,
                lname=specialist.lname,
                gender=specialist.gender,
                age=specialist.age,
                tag=specialist.tag if hasattr(specialist, 'tag') else [],
                about=specialist.about if hasattr(specialist, 'about') else "",
                educert=specialist.educert if hasattr(specialist, 'educert') else ""
            )
            specialists_data.append(specialist_info)
        
        return specialists_data
        
    except Exception as e:
        logger.exception(f"Error retrieving public specialists: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
