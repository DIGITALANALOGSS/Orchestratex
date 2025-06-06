from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    capabilities: Optional[Dict] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    capabilities: Optional[Dict] = None
    status: Optional[str] = None

class Agent(AgentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AgentResponse(BaseModel):
    data: Agent
    message: str = "Success"

class AgentListResponse(BaseModel):
    data: List[Agent]
    total: int
    message: str = "Success"
