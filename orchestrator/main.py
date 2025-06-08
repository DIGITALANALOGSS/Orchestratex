import asyncio
import logging
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from orchestratex.config import get_settings
from orchestratex.database import SessionLocal
from orchestratex.models.workflow import Workflow, WorkflowStage, WorkflowTask
from orchestratex.services.auth_service import get_current_user
from orchestratex.schemas.auth import User

app = FastAPI(title="Orchestratex", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowRequest(BaseModel):
    workflow_name: str
    parameters: Dict[str, Any]

class AgentMessage(BaseModel):
    agent_name: str
    message: str
    metadata: Dict[str, Any]

@app.post("/workflow/execute")
async def execute_workflow(request: WorkflowRequest, current_user: User = Depends(get_current_user)):
    """Execute a workflow with the given parameters."""
    try:
        db = SessionLocal()
        
        # Create workflow instance
        workflow = Workflow(
            name=request.workflow_name,
            parameters=request.parameters,
            created_by=current_user.id
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        
        # Initialize workflow stages
        await _initialize_workflow_stages(workflow, request.parameters)
        
        return {"workflow_id": workflow.id, "status": "started"}
    except Exception as e:
        logger.error(f"Workflow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _initialize_workflow_stages(workflow: Workflow, parameters: Dict[str, Any]):
    """Initialize all stages for the workflow."""
    # Load workflow configuration
    workflow_config = get_workflow_config(workflow.name)
    
    for stage_config in workflow_config.stages:
        stage = WorkflowStage(
            workflow_id=workflow.id,
            name=stage_config.name,
            status="pending"
        )
        workflow.stages.append(stage)
        
        # Create tasks for the stage
        await _create_stage_tasks(stage, stage_config, parameters)

async def _create_stage_tasks(stage: WorkflowStage, stage_config: Dict[str, Any], parameters: Dict[str, Any]):
    """Create tasks for a workflow stage."""
    for task_config in stage_config.tasks:
        task = WorkflowTask(
            stage_id=stage.id,
            agent_name=task_config.agent,
            parameters={
                **parameters,
                **task_config.parameters
            },
            status="pending"
        )
        stage.tasks.append(task)

@app.post("/agent/message")
async def handle_agent_message(message: AgentMessage):
    """Handle messages from agents."""
    try:
        db = SessionLocal()
        
        # Find the corresponding task
        task = db.query(WorkflowTask).filter(
            WorkflowTask.agent_name == message.agent_name,
            WorkflowTask.status == "pending"
        ).first()
        
        if not task:
            raise HTTPException(status_code=404, detail="No pending task found for this agent")
        
        # Update task status and result
        task.status = "completed"
        task.result = message.message
        task.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Process next stage if all tasks are complete
        await _process_next_stage(task.stage_id)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Agent message processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _process_next_stage(stage_id: int):
    """Process the next stage in the workflow."""
    db = SessionLocal()
    stage = db.query(WorkflowStage).get(stage_id)
    
    if not stage:
        return
    
    # Check if all tasks are complete
    all_complete = all(task.status == "completed" for task in stage.tasks)
    
    if all_complete:
        # Update stage status
        stage.status = "completed"
        stage.completed_at = datetime.utcnow()
        
        # Get next stage
        next_stage = db.query(WorkflowStage).filter(
            WorkflowStage.workflow_id == stage.workflow_id,
            WorkflowStage.id > stage.id
        ).order_by(WorkflowStage.id).first()
        
        if next_stage:
            # Initialize next stage
            await _initialize_stage(next_stage)
        else:
            # Complete workflow
            stage.workflow.status = "completed"
            stage.workflow.completed_at = datetime.utcnow()
        
        db.commit()

async def _initialize_stage(stage: WorkflowStage):
    """Initialize a stage by starting its tasks."""
    db = SessionLocal()
    
    for task in stage.tasks:
        if task.status == "pending":
            # Send task to agent
            await send_task_to_agent(task)

async def send_task_to_agent(task: WorkflowTask):
    """Send a task to an agent."""
    # Implementation will depend on the agent communication protocol
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
