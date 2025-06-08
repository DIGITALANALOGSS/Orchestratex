from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    stages = relationship("WorkflowStage", back_populates="workflow")
    metrics = relationship("WorkflowMetric", back_populates="workflow")

class WorkflowStage(Base):
    __tablename__ = "workflow_stages"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    workflow = relationship("Workflow", back_populates="stages")
    tasks = relationship("WorkflowTask", back_populates="stage")

class WorkflowTask(Base):
    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, index=True)
    stage_id = Column(Integer, ForeignKey("workflow_stages.id"))
    agent_name = Column(String)
    parameters = Column(JSON)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result = Column(JSON)
    
    stage = relationship("WorkflowStage", back_populates="tasks")

class WorkflowMetric(Base):
    __tablename__ = "workflow_metrics"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String)
    value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    workflow = relationship("Workflow", back_populates="metrics")

class AgentSession(Base):
    __tablename__ = "agent_sessions"

    id = Column(Integer, primary_key=True, index=True)
    agent_name = Column(String)
    session_id = Column(String, unique=True)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)

class AgentMetric(Base):
    __tablename__ = "agent_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("agent_sessions.session_id"))
    metric_name = Column(String)
    value = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("AgentSession", back_populates="metrics")
