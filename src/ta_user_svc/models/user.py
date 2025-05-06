from sqlalchemy import Column, String, Boolean
from ta_user_svc.models.base import Base

class User(Base):
    __tablename__ = "users"

    email = Column(String, primary_key=True, index=True)
    passhash = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)
    approved = Column(Boolean, default=False, nullable=False)
