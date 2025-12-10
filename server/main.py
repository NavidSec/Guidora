from fastapi import FastAPI
from test_router import router as test_router
from auth.sent_otp import router as sent_otp_router
from auth.verify_otp import router as verify_otp_router
from auth.set_info import router as set_info_router
from home.Homepage import router as homepage_router
from home.users import router as users_router
from profile.set_spe_profile import router as spe_profile_router
from profile.set_user_profile import router as user_profile_router
from reservation.set_spe_avi_slots import router as spe_slots_router
from reservation.set_user_slot import router as user_slots_router
app = FastAPI(title="Guidora App")
app.include_router(test_router, prefix="/test")
app.include_router(sent_otp_router, prefix="/auth")
app.include_router(verify_otp_router, prefix="/auth")
app.include_router(set_info_router, prefix="/auth")
app.include_router(homepage_router, prefix="/home")
app.include_router(users_router, prefix="/home")
app.include_router(spe_profile_router, prefix="/profile")
app.include_router(user_profile_router, prefix="/profile")
app.include_router(spe_slots_router, prefix="/reservation")
app.include_router(user_slots_router, prefix="/reservation")
