from fastapi import FastAPI
from auth.register import sent_otp, verify_otp

app = FastAPI(title="App")
app.include_router(sent_otp.router, prefix="/auth/register")
app.include_router(verify_otp.router, prefix="/auth/register")
#app.include_router(users.router, prefix="/home")
#app.include_router(set_profile.router, prefix="/profile")
