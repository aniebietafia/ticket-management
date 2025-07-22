from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    is_activated: Optional[bool] = None

class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    is_activated: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class UserToken(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserTokenData(BaseModel):
    id: str
    email: EmailStr

    class Config:
        from_attributes = True