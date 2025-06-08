from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.database.models import Content
from orchestratex.schemas.content import ContentCreate, ContentUpdate

class ContentService:
    def __init__(self, db: Session):
        self.db = db

    def get_content(self, content_id: int) -> Optional[Content]:
        """Get content by ID."""
        return self.db.query(Content).filter(Content.id == content_id).first()

    def get_contents(self, skip: int = 0, limit: int = 100) -> List[Content]:
        """Get list of contents."""
        return self.db.query(Content).offset(skip).limit(limit).all()

    def get_contents_by_session(self, session_id: int) -> List[Content]:
        """Get contents by session ID."""
        return self.db.query(Content).filter(Content.session_id == session_id).all()

    def create_content(self, content: ContentCreate) -> Content:
        """Create new content."""
        db_content = Content(
            session_id=content.session_id,
            title=content.title,
            content_type=content.content_type,
            difficulty_level=content.difficulty_level
        )
        self.db.add(db_content)
        self.db.commit()
        self.db.refresh(db_content)
        return db_content

    def update_content(self, content_id: int, content: ContentUpdate) -> Optional[Content]:
        """Update content."""
        db_content = self.get_content(content_id)
        if db_content:
            for key, value in content.model_dump(exclude_unset=True).items():
                setattr(db_content, key, value)
            self.db.commit()
            self.db.refresh(db_content)
        return db_content

    def delete_content(self, content_id: int) -> bool:
        """Delete content."""
        db_content = self.get_content(content_id)
        if db_content:
            self.db.delete(db_content)
            self.db.commit()
            return True
        return False
