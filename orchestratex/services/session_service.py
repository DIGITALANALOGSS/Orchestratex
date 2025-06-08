from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from orchestratex.database.models import LearningSession
from orchestratex.schemas.session import SessionCreate, SessionUpdate

class SessionService:
    def __init__(self, db: Session):
        self.db = db

    def get_session(self, session_id: int) -> Optional[LearningSession]:
        """Get session by ID."""
        return self.db.query(LearningSession).filter(LearningSession.id == session_id).first()

    def get_sessions(self, skip: int = 0, limit: int = 100) -> List[LearningSession]:
        """Get list of sessions."""
        return self.db.query(LearningSession).offset(skip).limit(limit).all()

    def get_sessions_by_user(self, user_id: int) -> List[LearningSession]:
        """Get sessions by user ID."""
        return self.db.query(LearningSession).filter(LearningSession.user_id == user_id).all()

    def create_session(self, session: SessionCreate) -> LearningSession:
        """Create new session."""
        db_session = LearningSession(
            user_id=session.user_id,
            topic=session.topic,
            start_time=datetime.utcnow(),
            engagement_score=session.engagement_score,
            progress_score=session.progress_score,
            quantum_simulation=session.quantum_simulation
        )
        self.db.add(db_session)
        self.db.commit()
        self.db.refresh(db_session)
        return db_session

    def update_session(self, session_id: int, session: SessionUpdate) -> Optional[LearningSession]:
        """Update session."""
        db_session = self.get_session(session_id)
        if db_session:
            for key, value in session.model_dump(exclude_unset=True).items():
                setattr(db_session, key, value)
            self.db.commit()
            self.db.refresh(db_session)
        return db_session

    def complete_session(self, session_id: int) -> Optional[LearningSession]:
        """Mark session as complete."""
        db_session = self.get_session(session_id)
        if db_session:
            db_session.end_time = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_session)
        return db_session

    def delete_session(self, session_id: int) -> bool:
        """Delete session."""
        db_session = self.get_session(session_id)
        if db_session:
            self.db.delete(db_session)
            self.db.commit()
            return True
        return False
