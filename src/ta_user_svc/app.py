from fastapi import FastAPI
from ta_user_svc.routers.user_registration import router as user_registration_router

app = FastAPI(debug=True)

app.include_router(user_registration_router, prefix="/api")
