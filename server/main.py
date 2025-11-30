from fastapi import FastAPI
from auth.register import sent_otp, verify_otp
from home import router as home_router  

app = FastAPI(title="App")
app.include_router(sent_otp.router, prefix="/auth")
app.include_router(verify_otp.router, prefix="/auth") 
app.include_router(home_router, prefix="/home")
#app.include_router(set_profile.router, prefix="/profile")
