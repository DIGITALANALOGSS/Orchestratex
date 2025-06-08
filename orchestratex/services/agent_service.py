from typing import List, Optional, Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from orchestratex.models.agent import Agent
from orchestratex.schemas.agent import AgentCreate, AgentUpdate
from orchestratex.database import get_db
from orchestratex.config import get_settings
from fastapi import WebSocket
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

class AgentService:
    def __init__(self, db: Session):
        self.db = db
        self.agent_connections: Dict[str, WebSocket] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.agent_queues: Dict[str, asyncio.Queue] = {}

    async def connect_agent(self, agent_name: str, websocket: WebSocket) -> None:
        """Register a new agent connection."""
        await websocket.accept()
        self.agent_connections[agent_name] = websocket
        self.agent_queues[agent_name] = asyncio.Queue()
        
        # Start task to handle incoming messages
        self.agent_tasks[agent_name] = asyncio.create_task(
            self._handle_agent_messages(agent_name, websocket)
        )

    async def disconnect_agent(self, agent_name: str) -> None:
        """Disconnect an agent."""
        if agent_name in self.agent_connections:
            await self.agent_connections[agent_name].close()
            del self.agent_connections[agent_name]
            del self.agent_queues[agent_name]
            
            if agent_name in self.agent_tasks:
                self.agent_tasks[agent_name].cancel()
                del self.agent_tasks[agent_name]

    async def _handle_agent_messages(self, agent_name: str, websocket: WebSocket) -> None:
        """Handle incoming messages from an agent."""
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Process the message
                await self.process_agent_message(agent_name, message)
        except Exception as e:
            logger.error(f"Error handling messages for {agent_name}: {str(e)}")
            await self.disconnect_agent(agent_name)

    async def process_agent_message(self, agent_name: str, message: Dict[str, Any]) -> None:
        """Process a message from an agent."""
        db_agent = self.get_agent_by_name(agent_name)
        if not db_agent:
            raise ValueError(f"Agent {agent_name} not found")

        # Update agent status
        await self.update_agent_status(db_agent.id, "active")
        
        # Process the message based on its type
        message_type = message.get("type")
        
        if message_type == "task_completed":
            await self._handle_task_completion(db_agent, message)
        elif message_type == "status_update":
            await self._handle_status_update(db_agent, message)
        elif message_type == "metric":
            await self._handle_metric(db_agent, message)

    async def _handle_task_completion(self, agent: Agent, message: Dict[str, Any]) -> None:
        """Handle task completion message."""
        task_id = message.get("task_id")
        result = message.get("result")
        
        # Update task status in database
        # Implementation depends on your database schema
        pass

    async def _handle_status_update(self, agent: Agent, message: Dict[str, Any]) -> None:
        """Handle agent status update."""
        new_status = message.get("status")
        
        # Update agent status in database
        # Implementation depends on your database schema
        pass

    async def _handle_metric(self, agent: Agent, message: Dict[str, Any]) -> None:
        """Handle agent metric reporting."""
        metric_name = message.get("metric_name")
        metric_value = message.get("metric_value")
        
        # Store metric in database
        # Implementation depends on your database schema
        pass

    async def send_task_to_agent(self, agent_name: str, task_data: Dict[str, Any]) -> None:
        """Send a task to an agent."""
        if agent_name not in self.agent_connections:
            raise ValueError(f"Agent {agent_name} not connected")

        await self.agent_connections[agent_name].send_text(
            json.dumps({"type": "task", "data": task_data})
        )

    async def broadcast_message(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected agents."""
        for websocket in self.agent_connections.values():
            try:
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")

    def create_agent(self, agent_data: AgentCreate) -> Agent:
        db_agent = Agent(**agent_data.model_dump())
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def get_agents(self, skip: int = 0, limit: int = 100) -> List[Agent]:
        return self.db.query(Agent).offset(skip).limit(limit).all()

    def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Optional[Agent]:
        db_agent = self.get_agent(agent_id)
        if db_agent:
            for key, value in agent_data.model_dump(exclude_unset=True).items():
                setattr(db_agent, key, value)
            self.db.commit()
            self.db.refresh(db_agent)
        return db_agent

    def delete_agent(self, agent_id: int) -> bool:
        db_agent = self.get_agent(agent_id)
        if db_agent:
            self.db.delete(db_agent)
            self.db.commit()
            return True
        return False

    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        return self.db.query(Agent).filter(Agent.name == name).first()

    def get_active_agents(self) -> List[Agent]:
        return self.db.query(Agent).filter(Agent.status == "active").all()

    def update_agent_status(self, agent_id: int, status: str) -> Optional[Agent]:
        db_agent = self.get_agent(agent_id)
        if db_agent:
            db_agent.status = status
            self.db.commit()
            self.db.refresh(db_agent)
        return db_agent
