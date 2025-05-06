import os
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

import jwt  # PyJWT
from passlib.context import CryptContext

from ta_user_svc.models.user import User
from ta_user_svc.models.base import get_db

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str

JWT_SECRET = os.getenv("JWT_SECRET", "mysecret")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10"))
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "1440"))

@router.post("/login", response_model=TokenResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == login_request.email).first()
        if not user or not pwd_context.verify(login_request.password, user.passhash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.approved:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User not approved")

        now = datetime.utcnow()
        access_payload = {
            "sub": user.email,
            "nickname": user.nickname,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        refresh_payload = {
            "sub": user.email,
            "nickname": user.nickname,
            "exp": now + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
        }
        access_token = jwt.encode(access_payload, JWT_SECRET, algorithm="HS256")
        refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm="HS256")
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
