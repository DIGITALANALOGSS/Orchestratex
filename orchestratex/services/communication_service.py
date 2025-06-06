from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.models.communication import Message
from orchestratex.schemas.communication import MessageCreate
from orchestratex.database import get_db
from orchestratex.config import get_settings
from orchestratex.utils.redis_utils import RedisManager

settings = get_settings()

class CommunicationService:
    def __init__(self, db: Session):
        self.db = db
        self.redis_manager = RedisManager()

    def send_message(self, message_data: MessageCreate) -> Message:
        db_message = Message(**message_data.model_dump())
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        # Publish message to Redis for real-time updates
        self.redis_manager.publish_message(
            f"agent_{message_data.receiver_id}_messages",
            db_message
        )
        
        return db_message

    def get_messages(self, agent_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return self.db.query(Message).filter(
            (Message.sender_id == agent_id) | (Message.receiver_id == agent_id)
        ).offset(skip).limit(limit).all()

    def get_conversation(self, sender_id: int, receiver_id: int) -> List[Message]:
        return self.db.query(Message).filter(
            ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
            ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
        ).order_by(Message.created_at).all()

    def get_unread_messages(self, agent_id: int) -> List[Message]:
        return self.db.query(Message).filter(
            Message.receiver_id == agent_id,
            Message.metadata['read'].astext.cast(Boolean) == False
        ).all()

    def mark_message_as_read(self, message_id: int) -> Optional[Message]:
        message = self.db.query(Message).filter(Message.id == message_id).first()
        if message:
            message.metadata['read'] = True
            self.db.commit()
            self.db.refresh(message)
        return message

    def subscribe_to_messages(self, agent_id: int):
        """Subscribe to real-time messages for an agent"""
        return self.redis_manager.subscribe(f"agent_{agent_id}_messages")
