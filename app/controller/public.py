from fastapi import APIRouter


router = APIRouter(tags=["Public"])


@router.get("/")
async def root():
    """Welcome endpoint"""
    return {"message": "FastAPI Ticket Management API", "version": "1.0.0"}
