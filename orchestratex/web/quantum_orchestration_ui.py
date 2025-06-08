from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import json
import logging
from orchestratex.demo.quantum_orchestration_demo import QuantumOrchestrationDemo

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quantum Orchestration Demo")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

class WorkflowRequest(BaseModel):
    user_id: str
    user_role: str
    data: str
    circuit: Optional[str] = "Hadamard + CNOT"
    state: Optional[str] = "Bell State"

class Badge(BaseModel):
    name: str
    description: str
    points: int
    metadata: Dict[str, Any]

class ProgressResponse(BaseModel):
    badges: List[Badge]
    total_points: int
    last_award: Optional[str]
    achievements: List[str]

class QuantumDemo:
    """Web interface for quantum orchestration demo."""
    
    def __init__(self):
        self.demo = QuantumOrchestrationDemo()
        self._initialize_routes()
        
    def _initialize_routes(self) -> None:
        """Initialize API routes."""
        @app.get("/", response_class=HTMLResponse)
        async def home(request: Request):
            return templates.TemplateResponse(
                "index.html",
                {"request": request}
            )
            
        @app.post("/run_workflow")
        async def run_workflow(request: WorkflowRequest):
            try:
                result = await self.demo.run_quantum_workflow(
                    user_id=request.user_id,
                    user_role=request.user_role,
                    data=request.data
                )
                return JSONResponse(content=result)
                
            except PermissionError as e:
                raise HTTPException(status_code=403, detail=str(e))
                
            except Exception as e:
                logger.error(f"Workflow failed: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/progress/{user_id}")
        async def get_progress(user_id: str):
            try:
                game = self.demo.registry.get("Engagement")
                badges = await game.get_progress(user_id)
                
                # Calculate total points
                total_points = sum(badge.get("points", 0) for badge in badges)
                
                # Get last award timestamp
                last_award = badges[-1].get("timestamp") if badges else None
                
                # Get achievements
                achievements = [badge.get("name") for badge in badges]
                
                return ProgressResponse(
                    badges=badges,
                    total_points=total_points,
                    last_award=last_award,
                    achievements=achievements
                )
                
            except Exception as e:
                logger.error(f"Failed to get progress: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
        @app.get("/quantum_concepts")
        async def get_quantum_concepts():
            try:
                quantum = self.demo.registry.get("Quantum")
                concepts = quantum.explain_quantum()
                return JSONResponse(content={"concepts": concepts})
                
            except Exception as e:
                logger.error(f"Failed to get quantum concepts: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
                
    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Run the web server."""
        logger.info(f"Starting Quantum Orchestration UI on {host}:{port}")
        uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    demo = QuantumDemo()
    demo.run()
