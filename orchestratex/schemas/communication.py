from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: Dict
    type: str
    metadata: Optional[Dict] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    data: Message
    message: str = "Success"

class MessageListResponse(BaseModel):
    data: List[Message]
    total: int
    message: str = "Success"
