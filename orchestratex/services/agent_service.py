from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.models.agent import Agent
from orchestratex.schemas.agent import AgentCreate, AgentUpdate
from orchestratex.database import get_db
from orchestratex.config import get_settings

settings = get_settings()

class AgentService:
    def __init__(self, db: Session):
        self.db = db

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
