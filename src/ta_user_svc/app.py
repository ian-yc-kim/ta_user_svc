from fastapi import FastAPI
from ta_user_svc.routers.user_registration import router as user_registration_router
from ta_user_svc.routers.user_login import router as user_login_router
from ta_user_svc.routers.user_logout import router as user_logout_router
from ta_user_svc.routers.user_refresh import router as user_refresh_router  # newly added

app = FastAPI(debug=True)

app.include_router(user_registration_router, prefix="/api")
app.include_router(user_login_router, prefix="/api")
app.include_router(user_logout_router, prefix="/api")
app.include_router(user_refresh_router, prefix="/api")  # token refresh endpoint
