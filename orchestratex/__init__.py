from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestratex.config import settings
from orchestratex.api import api_router
from orchestratex.services.agent_service import AgentService
from orchestratex.services.task_service import TaskService
from orchestratex.services.communication_service import CommunicationService
from orchestratex.database import get_db
from sqlalchemy.orm import Session

app = FastAPI(
    title="Orchestratex",
    description="Next-generation multi-agent orchestration platform",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection for services
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    app.state.agent_service = AgentService(db)
    app.state.task_service = TaskService(db)
    app.state.communication_service = CommunicationService(db)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "Next-generation multi-agent orchestration platform"
    }
