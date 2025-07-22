import uuid
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import settings

database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql//", "postgresql+asyncpg://")

engine = create_async_engine(database_url, echo=True)
AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"


# Ensure the database URL is correctly formatted for asyncpg
if not database_url.startswith("postgresql+asyncpg://"):
    raise ValueError("Database URL must start with 'postgresql+asyncpg://' for asyncpg support.")

class User(BaseModel):
    __tablename__ = "users"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_activated = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True, default=None)

    def __repr__(self):
        return f"<User id={self.id} email={self.email} is_active={self.is_activated}>"


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()