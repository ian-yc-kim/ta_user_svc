import logging
import re
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
from passlib.hash import bcrypt_sha256

from ta_user_svc.models.base import get_db
from ta_user_svc.models.user import User

router = APIRouter()

# Constant for nickname regex pattern
NICKNAME_REGEX = r"[A-Za-z0-9_.-]+"


class UserRegistrationRequest(BaseModel):
    email: str
    password: str
    nickname: str


class UserResponse(BaseModel):
    email: str
    nickname: str
    role: str
    approved: bool


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)

def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    try:
        # Validate email format with deliverability check disabled. Performing this before DB lookup.
        try:
            validate_email(request.email, check_deliverability=False)
        except EmailNotValidError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Check for duplicate email
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered.")

        # Validate password: length and at least one letter
        if not (8 <= len(request.password) <= 32):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be between 8 and 32 characters.")
        if not any(c.isalpha() for c in request.password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one letter.")

        # Validate nickname: length and allowed characters
        if not (4 <= len(request.nickname) <= 32):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname must be between 4 and 32 characters.")
        if not re.fullmatch(NICKNAME_REGEX, request.nickname):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nickname can only contain letters, digits, dash (-), underscore (_) and dot (.) characters.")

        # Hash password using bcrypt_sha256 for improved security
        try:
            passhash = bcrypt_sha256.hash(request.password)
        except Exception as hash_exception:
            logging.error(hash_exception, exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error hashing password")

        new_user = User(
            email=request.email,
            passhash=passhash,
            nickname=request.nickname,
            role="user",
            approved=False
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse(
            email=new_user.email,
            nickname=new_user.nickname,
            role=new_user.role,
            approved=new_user.approved
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logging.error(e, exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
