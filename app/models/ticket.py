import uuid
import enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from config import settings
# import os

database_url = settings.database_url

# if database_url.startswith("postgresql://") and os.environ.get("ALEMBIC_RUNNING"):
#     database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(database_url, echo=True)
AsyncSessionLocal: sessionmaker[AsyncSession] = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
Base = declarative_base()

# engine = None
# AsyncSessionLocal = None

# def init_async_db():
#     global engine, AsyncSessionLocal
#     engine = create_async_engine(database_url, echo=True)
#     AsyncSessionLocal = sessionmaker(
#         bind=engine,
#         class_=AsyncSession,
#         expire_on_commit=False,
#     )

class TicketStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    RESOLVED = "Resolved"
    CLOSED = "Closed"

class BaseModel(Base):
    __abstract__ = True

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"

class User(BaseModel):
    __tablename__ = "users"

    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    is_activated = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True, default=None)
    role = Column(String(20), nullable=False, default="customer")

    def __repr__(self):
        return f"<User id={self.id} email={self.email} is_active={self.is_activated}>"

class Ticket(BaseModel):
    __tablename__ = "tickets"

    title = Column(String(100), nullable=False)
    description = Column(String, nullable=False)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    customer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    agent_id = Column(String(36), ForeignKey("users.id"), nullable=True, default=None)
    resolution_notes = Column(String, nullable=True)
    embed_token = Column(String, unique=True, nullable=False, default=lambda: str(uuid.uuid4()))

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()