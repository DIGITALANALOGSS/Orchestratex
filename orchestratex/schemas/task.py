from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: str
    priority: int = 1
    parameters: Optional[Dict] = None

class TaskCreate(TaskBase):
    agent_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    parameters: Optional[Dict] = None
    result: Optional[Dict] = None

class Task(TaskBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    agent_id: int
    
    class Config:
        from_attributes = True

class TaskResponse(BaseModel):
    data: Task
    message: str = "Success"

class TaskListResponse(BaseModel):
    data: List[Task]
    total: int
    message: str = "Success"
