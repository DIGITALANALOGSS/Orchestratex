from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.database.models import Feedback
from orchestratex.schemas.feedback import FeedbackCreate, FeedbackUpdate

class FeedbackService:
    def __init__(self, db: Session):
        self.db = db

    def get_feedback(self, feedback_id: int) -> Optional[Feedback]:
        """Get feedback by ID."""
        return self.db.query(Feedback).filter(Feedback.id == feedback_id).first()

    def get_feedbacks(self, skip: int = 0, limit: int = 100) -> List[Feedback]:
        """Get list of feedbacks."""
        return self.db.query(Feedback).offset(skip).limit(limit).all()

    def get_feedbacks_by_content(self, content_id: int) -> List[Feedback]:
        """Get feedbacks by content ID."""
        return self.db.query(Feedback).filter(Feedback.content_id == content_id).all()

    def get_feedbacks_by_user(self, user_id: int) -> List[Feedback]:
        """Get feedbacks by user ID."""
        return self.db.query(Feedback).filter(Feedback.user_id == user_id).all()

    def create_feedback(self, feedback: FeedbackCreate) -> Feedback:
        """Create new feedback."""
        db_feedback = Feedback(
            content_id=feedback.content_id,
            user_id=feedback.user_id,
            rating=feedback.rating,
            comment=feedback.comment
        )
        self.db.add(db_feedback)
        self.db.commit()
        self.db.refresh(db_feedback)
        return db_feedback

    def update_feedback(self, feedback_id: int, feedback: FeedbackUpdate) -> Optional[Feedback]:
        """Update feedback."""
        db_feedback = self.get_feedback(feedback_id)
        if db_feedback:
            for key, value in feedback.model_dump(exclude_unset=True).items():
                setattr(db_feedback, key, value)
            self.db.commit()
            self.db.refresh(db_feedback)
        return db_feedback

    def delete_feedback(self, feedback_id: int) -> bool:
        """Delete feedback."""
        db_feedback = self.get_feedback(feedback_id)
        if db_feedback:
            self.db.delete(db_feedback)
            self.db.commit()
            return True
        return False
