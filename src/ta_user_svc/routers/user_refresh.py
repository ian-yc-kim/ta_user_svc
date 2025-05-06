import os
import logging
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

import jwt

router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "mysecret")
ACCESS_TOKEN_EXPIRE_MINUTES = 10

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_req: RefreshRequest):
    try:
        # Placeholder for rate limiting: integrate proper rate limiter here.
        decoded_payload = jwt.decode(refresh_req.refresh_token, JWT_SECRET, algorithms=["HS256"])
        user_email = decoded_payload.get("sub")
        nickname = decoded_payload.get("nickname")
        if not user_email or not nickname:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
        now = datetime.utcnow()
        new_payload = {
            "sub": user_email,
            "nickname": nickname,
            "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        new_access_token = jwt.encode(new_payload, JWT_SECRET, algorithm="HS256")
        return TokenResponse(access_token=new_access_token)
    except jwt.ExpiredSignatureError as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except jwt.InvalidTokenError as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable")
