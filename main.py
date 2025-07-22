from fastapi import FastAPI
from contextlib import asynccontextmanager

from database import engine, Base
from controllers.auth_controller import router as auth_router
from controllers.user_controller import router as user_router
from controllers.public_controller import router as public_router
from controllers.ticket_controller import router as ticket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Cleanup on shutdown
    await engine.dispose()


app = FastAPI(
    title="FastAPI Ticket Management API",
    description="A clean, modular FastAPI application with JWT authentication using AsyncPG",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(public_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(ticket_router)
