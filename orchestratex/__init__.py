from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from orchestratex.config import settings
from orchestratex.api import api_router

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

# Include API router
app.include_router(api_router, prefix="/api/v1")
