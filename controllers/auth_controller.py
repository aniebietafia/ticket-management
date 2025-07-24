from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from database import get_db
from schemas import UserCreate, UserResponse, UserToken, UserLogin
from auth import auth_service
from user_service import user_service
from config import settings
from datetime import datetime


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    if await user_service.is_email_taken(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        db_user = await user_service.create_user(db=db, user=user)
        user_response = UserResponse.model_validate(db_user)
        return {
            "status": "success",
            "status_code": status.HTTP_201_CREATED,
            "message": "User created successfully",
            "user": user_response.model_dump()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.post("/login")
async def login_for_access_token(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT token"""
    email = payload.email
    password = payload.password

    user = await auth_service.authenticate_user(db, email, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login time
    user.last_login = datetime.now()
    await db.commit()
    await db.refresh(user)

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    # Prepare user data to return
    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_activated": user.is_activated,
        "last_login": user.last_login,
        "role": user.role,
        "token_type": "bearer",
        "access_token": access_token,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }

    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Login successful",
        "user": user_data
    }
