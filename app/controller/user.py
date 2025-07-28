from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.ticket import get_db, User
from app.schemas.ticket import UserResponse, UserUpdate
from app.api.user import user_service
from app.config.dependencies import get_current_active_user


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    user_data = {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "email": current_user.email,
        "is_activated": current_user.is_activated,
        "last_login": current_user.last_login,
    }
    """Get current user profile"""
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "User profile retrieved successfully",
        "user": user_data.model_dump()
    }


@router.put("/me")
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    updated_user = await user_service.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "User profile updated successfully",
        "user": updated_user.model_dump(exclude={"hashed_password"})
    }


@router.get("/all-users")
async def read_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get list of users (protected endpoint)"""
    users = await user_service.get_users(db, skip=skip, limit=limit)
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "Users retrieved successfully",
        "users": [user.model_dump(exclude={"hashed_password"}) for user in users]
    }


@router.get("/{user_id}")
async def read_user(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (protected endpoint)"""
    user = await user_service.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {
        "status": "success",
        "status_code": status.HTTP_200_OK,
        "message": "User retrieved successfully",
        "user": user.model_dump(exclude={"hashed_password"})
    }
