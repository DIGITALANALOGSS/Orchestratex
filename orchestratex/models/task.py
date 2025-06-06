from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from orchestratex.database import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    status = Column(String, default="pending")  # pending, in_progress, completed, failed
    priority = Column(Integer, default=1)
    parameters = Column(JSON)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    agent_id = Column(Integer, ForeignKey("agents.id"))
    agent = relationship("Agent", back_populates="tasks")
    
    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}', status='{self.status}')"
