from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from orchestratex.config import settings
from orchestratex.api import api_router
from orchestratex.services.agent_service import AgentService
from orchestratex.services.task_service import TaskService
from orchestratex.services.communication_service import CommunicationService
from orchestratex.services.auth_service import AuthService
from orchestratex.database import get_db
from orchestratex.schemas.auth import TokenData

app = FastAPI(
    title="Orchestratex",
    description="Next-generation multi-agent orchestration platform",
    version="0.1.0"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    app.state.auth_service = AuthService(db)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    auth_service = app.state.auth_service
    user = auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_superuser(current_user: User = Depends(get_current_active_user)):
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user

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
