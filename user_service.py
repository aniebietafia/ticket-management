from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import User
from schemas import UserCreate, UserUpdate
from auth import auth_service
from typing import Optional, List


class UserService:
    def __init__(self):
        self.auth_service = auth_service

    async def create_user(self, db: AsyncSession, user: UserCreate) -> User:
        """Create a new user"""
        hashed_password = self.auth_service.get_password_hash(user.password)
        db_user = User(
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            hashed_password=hashed_password,
            role=user.role or "customer"
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_user(self, db: AsyncSession, user_id: str) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        """Get list of users with pagination"""
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    async def update_user(self, db: AsyncSession, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = await self.get_user(db, user_id)
        if not db_user:
            return None

        update_data = user_update.model_dump(exclude_unset=True)

        # Handle password update separately
        if "password" in update_data:
            update_data["hashed_password"] = self.auth_service.get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def delete_user(self, db: AsyncSession, user_id: str) -> bool:
        """Delete user"""
        db_user = await self.get_user(db, user_id)
        if not db_user:
            return False

        await db.delete(db_user)
        await db.commit()
        return True

    async def is_email_taken(self, db: AsyncSession, email: str) -> bool:
        """Check if email is already taken"""
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none() is not None


# Global instance
user_service = UserService()
