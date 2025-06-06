from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from orchestratex.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("agents.id"))
    receiver_id = Column(Integer, ForeignKey("agents.id"))
    content = Column(JSON)
    type = Column(String)  # e.g., "text", "command", "event"
    metadata = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sender = relationship("Agent", foreign_keys=[sender_id])
    receiver = relationship("Agent", foreign_keys=[receiver_id])
    
    def __repr__(self):
        return f"Message(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id})"
