from fastapi import APIRouter
from orchestratex.config import get_settings

api_router = APIRouter()

@api_router.get("/")
async def root():
    settings = get_settings()
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Next-generation multi-agent orchestration platform"
    }
