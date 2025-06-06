from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from orchestratex.config import get_settings
from orchestratex.database import get_db
from orchestratex.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentResponse, AgentListResponse
from orchestratex.schemas.task import Task, TaskCreate, TaskUpdate, TaskResponse, TaskListResponse
from orchestratex.schemas.communication import Message, MessageCreate, MessageResponse, MessageListResponse
from orchestratex.services.agent_service import AgentService
from orchestratex.services.task_service import TaskService
from orchestratex.services.communication_service import CommunicationService

api_router = APIRouter()

# Agent endpoints
@api_router.post("/agents", response_model=AgentResponse)
async def create_agent(agent: AgentCreate, db: Session = Depends(get_db)):
    agent_service = AgentService(db)
    db_agent = agent_service.create_agent(agent)
    return {"data": db_agent}

@api_router.get("/agents", response_model=AgentListResponse)
async def read_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    agent_service = AgentService(db)
    agents = agent_service.get_agents(skip, limit)
    return {"data": agents, "total": len(agents)}

@api_router.get("/agents/{agent_id}", response_model=AgentResponse)
async def read_agent(agent_id: int, db: Session = Depends(get_db)):
    agent_service = AgentService(db)
    db_agent = agent_service.get_agent(agent_id)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"data": db_agent}

@api_router.put("/agents/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: int, agent: AgentUpdate, db: Session = Depends(get_db)):
    agent_service = AgentService(db)
    db_agent = agent_service.update_agent(agent_id, agent)
    if db_agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"data": db_agent}

@api_router.delete("/agents/{agent_id}", response_model=AgentResponse)
async def delete_agent(agent_id: int, db: Session = Depends(get_db)):
    agent_service = AgentService(db)
    db_agent = agent_service.delete_agent(agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"data": db_agent}

# Task endpoints
@api_router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    db_task = task_service.create_task(task)
    return {"data": db_task}

@api_router.get("/tasks", response_model=TaskListResponse)
async def read_tasks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    tasks = task_service.get_tasks(skip, limit)
    return {"data": tasks, "total": len(tasks)}

@api_router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(task_id: int, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    db_task = task_service.get_task(task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": db_task}

@api_router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(task_id: int, task: TaskUpdate, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    db_task = task_service.update_task(task_id, task)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": db_task}

@api_router.delete("/tasks/{task_id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    task_service = TaskService(db)
    db_task = task_service.delete_task(task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"data": db_task}

# Communication endpoints
@api_router.post("/messages", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: Session = Depends(get_db)):
    communication_service = CommunicationService(db)
    db_message = communication_service.send_message(message)
    return {"data": db_message}

@api_router.get("/messages", response_model=MessageListResponse)
async def read_messages(agent_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    communication_service = CommunicationService(db)
    messages = communication_service.get_messages(agent_id, skip, limit)
    return {"data": messages, "total": len(messages)}

@api_router.get("/messages/conversation", response_model=MessageListResponse)
async def read_conversation(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    communication_service = CommunicationService(db)
    messages = communication_service.get_conversation(sender_id, receiver_id)
    return {"data": messages, "total": len(messages)}
