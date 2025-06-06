from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.models.task import Task
from orchestratex.schemas.task import TaskCreate, TaskUpdate
from orchestratex.database import get_db
from orchestratex.config import get_settings

settings = get_settings()

class TaskService:
    def __init__(self, db: Session):
        self.db = db

    def create_task(self, task_data: TaskCreate) -> Task:
        db_task = Task(**task_data.model_dump())
        self.db.add(db_task)
        self.db.commit()
        self.db.refresh(db_task)
        return db_task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.db.query(Task).filter(Task.id == task_id).first()

    def get_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        return self.db.query(Task).offset(skip).limit(limit).all()

    def update_task(self, task_id: int, task_data: TaskUpdate) -> Optional[Task]:
        db_task = self.get_task(task_id)
        if db_task:
            for key, value in task_data.model_dump(exclude_unset=True).items():
                setattr(db_task, key, value)
            self.db.commit()
            self.db.refresh(db_task)
        return db_task

    def delete_task(self, task_id: int) -> bool:
        db_task = self.get_task(task_id)
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False

    def get_tasks_by_status(self, status: str) -> List[Task]:
        return self.db.query(Task).filter(Task.status == status).all()

    def get_tasks_by_agent(self, agent_id: int) -> List[Task]:
        return self.db.query(Task).filter(Task.agent_id == agent_id).all()

    def get_pending_tasks(self) -> List[Task]:
        return self.db.query(Task).filter(Task.status == "pending").all()

    def update_task_status(self, task_id: int, status: str) -> Optional[Task]:
        db_task = self.get_task(task_id)
        if db_task:
            db_task.status = status
            self.db.commit()
            self.db.refresh(db_task)
        return db_task
