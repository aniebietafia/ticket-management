from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class UserCreate(BaseModel):
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: Optional[str] = Field("customer", max_length=20)
    is_activated: Optional[bool] = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = None
    is_activated: Optional[bool] = None
    role: Optional[str] = Field(None, max_length=20)

class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: EmailStr
    is_activated: bool
    last_login: Optional[datetime] = None
    role: str
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


class TicketBase(BaseModel):
    title: str
    description: str

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    resolution_notes: Optional[str] = None

class TicketAssign(BaseModel):
    agent_id: str

class TicketResponse(TicketBase):
    id: str
    status: TicketStatus
    created_at: datetime
    updated_at: Optional[datetime]
    customer_id: str
    agent_id: Optional[str]
    resolution_notes: Optional[str]
    embed_token: str

    class Config:
        from_attributes = True