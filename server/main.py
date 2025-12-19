from fastapi import FastAPI

app = FastAPI(title="Guidora App")


@app.get("/")
def read_root():
    return {"Welcome to Guidora API!  Navidsec Inc."}


# --- Test Router ---
from test_router import router as test_router

# --- Auth Routers ---
from auth.send_otp import router as send_otp_router
from auth.verify_otp import router as verify_otp_router
from auth.set_info import router as set_info_router
from auth.check_jwt import router as check_jwt_router

# --- Home Routers ---
from home.homepage import router as homepage_router
from home.users import router as users_router

# --- Profile Routers ---
from profile.set_spe_profile import router as spe_profile_router
from profile.set_user_profile import router as user_profile_router

# --- Reservation Routers ---
from reservation.set_spe_avi_slots import router as spe_slots_router
from reservation.set_user_slot import router as user_slots_router


# --- Include Routers ---

# Test routes (ping, health check, etc.)
app.include_router(test_router, prefix="/test")

# Auth routes (OTP, registration, user info)
app.include_router(send_otp_router, prefix="/auth")
app.include_router(verify_otp_router, prefix="/auth")
app.include_router(set_info_router, prefix="/auth")
app.include_router(check_jwt_router, prefix="/auth")

# Home routes (homepage, user listings)
app.include_router(homepage_router, prefix="/home")
app.include_router(users_router, prefix="/home")

# Profile routes (specialist and user profiles)
app.include_router(spe_profile_router, prefix="/profile")
app.include_router(user_profile_router, prefix="/profile")

# Reservation routes (specialist and user slots)
app.include_router(spe_slots_router, prefix="/reservation")
app.include_router(user_slots_router, prefix="/reservation")