from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.database.models import UserProfile
from orchestratex.schemas.profile import ProfileCreate, ProfileUpdate

class ProfileService:
    def __init__(self, db: Session):
        self.db = db

    def get_profile(self, profile_id: int) -> Optional[UserProfile]:
        """Get profile by ID."""
        return self.db.query(UserProfile).filter(UserProfile.id == profile_id).first()

    def get_profiles(self, skip: int = 0, limit: int = 100) -> List[UserProfile]:
        """Get list of profiles."""
        return self.db.query(UserProfile).offset(skip).limit(limit).all()

    def get_profile_by_user(self, user_id: int) -> Optional[UserProfile]:
        """Get profile by user ID."""
        return self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    def create_profile(self, profile: ProfileCreate) -> UserProfile:
        """Create new profile."""
        db_profile = UserProfile(
            user_id=profile.user_id,
            learning_style=profile.learning_style,
            preferred_modality=profile.preferred_modality,
            current_level=profile.current_level,
            strengths=profile.strengths,
            gaps=profile.gaps
        )
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update_profile(self, profile_id: int, profile: ProfileUpdate) -> Optional[UserProfile]:
        """Update profile."""
        db_profile = self.get_profile(profile_id)
        if db_profile:
            for key, value in profile.model_dump(exclude_unset=True).items():
                setattr(db_profile, key, value)
            self.db.commit()
            self.db.refresh(db_profile)
        return db_profile

    def delete_profile(self, profile_id: int) -> bool:
        """Delete profile."""
        db_profile = self.get_profile(profile_id)
        if db_profile:
            self.db.delete(db_profile)
            self.db.commit()
            return True
        return False
