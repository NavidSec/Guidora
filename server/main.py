from fastapi import FastAPI

app = FastAPI(title="Guidora App")

@app.get("/")
def read_root():
    return {"message": "Welcome to Guidora API! Navidsec Inc."}

# --- Auth Routers ---
from auth.send_otp import router as send_otp_router
from auth.verify_otp import router as verify_otp_router
from auth.set_info import router as set_info_router
from auth.check_jwt import router as check_jwt_router

# --- Home Routers ---
from home.homepage import router as homepage_router
from home.get_spe_info import router as get_spe_info_router

# --- Profile Routers ---
from profile.set_spe_profile import router as spe_profile_router
from profile.set_user_profile import router as user_profile_router

# --- Reservation Routers ---
from reservation.set_spe_avi_slots import router as spe_slots_router
from reservation.set_user_slot import router as user_slots_router
from reservation.get_reserved_slots import router as get_reserved_slots_router
from reservation.del_reserved_slots import router as del_reserved_slots_router  # <-- اصلاح شد

# --- Include Routers ---

# Auth routes
app.include_router(send_otp_router, prefix="/auth", tags=["Auth"])
app.include_router(verify_otp_router, prefix="/auth", tags=["Auth"])
app.include_router(set_info_router, prefix="/auth", tags=["Auth"])
app.include_router(check_jwt_router, prefix="/auth", tags=["Auth"])

# Home routes
app.include_router(homepage_router, prefix="/home", tags=["Home"])
app.include_router(get_spe_info_router, prefix="/home", tags=["Home"]) 

# Profile routes
app.include_router(spe_profile_router, prefix="/profile", tags=["Profile"])
app.include_router(user_profile_router, prefix="/profile", tags=["Profile"])

# Reservation routes
app.include_router(spe_slots_router, prefix="/reservation", tags=["Reservation"])
app.include_router(user_slots_router, prefix="/reservation", tags=["Reservation"])
app.include_router(get_reserved_slots_router, prefix="/reservation", tags=["Reservation"])
app.include_router(del_reserved_slots_router, prefix="/reservation", tags=["Reservation"])  # <-- اصلاح شد
