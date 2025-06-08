from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.database.models import Assessment
from orchestratex.schemas.assessment import AssessmentCreate, AssessmentUpdate

class AssessmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_assessment(self, assessment_id: int) -> Optional[Assessment]:
        """Get assessment by ID."""
        return self.db.query(Assessment).filter(Assessment.id == assessment_id).first()

    def get_assessments(self, skip: int = 0, limit: int = 100) -> List[Assessment]:
        """Get list of assessments."""
        return self.db.query(Assessment).offset(skip).limit(limit).all()

    def get_assessments_by_session(self, session_id: int) -> List[Assessment]:
        """Get assessments by session ID."""
        return self.db.query(Assessment).filter(Assessment.session_id == session_id).all()

    def get_assessments_by_profile(self, profile_id: int) -> List[Assessment]:
        """Get assessments by profile ID."""
        return self.db.query(Assessment).filter(Assessment.profile_id == profile_id).all()

    def create_assessment(self, assessment: AssessmentCreate) -> Assessment:
        """Create new assessment."""
        db_assessment = Assessment(
            profile_id=assessment.profile_id,
            session_id=assessment.session_id,
            question=assessment.question,
            answer=assessment.answer,
            correct=assessment.correct,
            feedback=assessment.feedback
        )
        self.db.add(db_assessment)
        self.db.commit()
        self.db.refresh(db_assessment)
        return db_assessment

    def update_assessment(self, assessment_id: int, assessment: AssessmentUpdate) -> Optional[Assessment]:
        """Update assessment."""
        db_assessment = self.get_assessment(assessment_id)
        if db_assessment:
            for key, value in assessment.model_dump(exclude_unset=True).items():
                setattr(db_assessment, key, value)
            self.db.commit()
            self.db.refresh(db_assessment)
        return db_assessment

    def delete_assessment(self, assessment_id: int) -> bool:
        """Delete assessment."""
        db_assessment = self.get_assessment(assessment_id)
        if db_assessment:
            self.db.delete(db_assessment)
            self.db.commit()
            return True
        return False
