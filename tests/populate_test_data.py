import random
import string
from datetime import datetime, timedelta
from typing import List
from orchestratex.database import get_db, init_db
from orchestratex.database.models import User, UserProfile, LearningSession, Content, Assessment, QuantumState, Feedback
from orchestratex.services import (
    UserService,
    ProfileService,
    SessionService,
    ContentService,
    AssessmentService,
    QuantumService,
    FeedbackService
)

def generate_random_string(length: int) -> str:
    """Generate a random string."""
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def create_test_users(db: Session, count: int = 5) -> List[User]:
    """Create test users."""
    users = []
    user_service = UserService(db)
    
    for i in range(count):
        username = f"user{i+1}_{generate_random_string(5)}"
        email = f"user{i+1}@example.com"
        password = "password123"
        
        user = user_service.create_user(UserCreate(
            username=username,
            email=email,
            password=password
        ))
        users.append(user)
    
    return users

def create_test_profiles(db: Session, users: List[User]) -> List[UserProfile]:
    """Create test user profiles."""
    profiles = []
    profile_service = ProfileService(db)
    
    learning_styles = ["visual", "auditory", "kinesthetic"]
    modalities = ["text", "video", "interactive"]
    
    for user in users:
        profile = profile_service.create_profile(ProfileCreate(
            user_id=user.id,
            learning_style=random.choice(learning_styles),
            preferred_modality=random.choice(modalities),
            current_level="beginner",
            strengths="[]",
            gaps="[]"
        ))
        profiles.append(profile)
    
    return profiles

def create_test_sessions(db: Session, users: List[User]) -> List[LearningSession]:
    """Create test learning sessions."""
    sessions = []
    session_service = SessionService(db)
    
    topics = [
        "quantum computing basics",
        "quantum algorithms",
        "quantum cryptography",
        "quantum simulation",
        "quantum error correction"
    ]
    
    for user in users:
        for i in range(3):
            session = session_service.create_session(SessionCreate(
                user_id=user.id,
                topic=random.choice(topics),
                engagement_score=random.uniform(0.5, 1.0),
                progress_score=random.uniform(0.3, 0.9),
                quantum_simulation=True
            ))
            sessions.append(session)
    
    return sessions

def create_test_content(db: Session, sessions: List[LearningSession]) -> List[Content]:
    """Create test learning content."""
    content = []
    content_service = ContentService(db)
    
    content_types = ["text", "video", "interactive", "quiz", "simulation"]
    difficulty_levels = ["beginner", "intermediate", "advanced"]
    
    for session in sessions:
        for i in range(2):
            content_item = content_service.create_content(ContentCreate(
                session_id=session.id,
                title=f"Content {i+1} for {session.topic}",
                content_type=random.choice(content_types),
                difficulty_level=random.choice(difficulty_levels)
            ))
            content.append(content_item)
    
    return content

def create_test_assessments(db: Session, sessions: List[LearningSession]) -> List[Assessment]:
    """Create test assessments."""
    assessments = []
    assessment_service = AssessmentService(db)
    
    for session in sessions:
        for i in range(5):
            assessment = assessment_service.create_assessment(AssessmentCreate(
                profile_id=session.user_id,
                session_id=session.id,
                question=f"Question {i+1} about {session.topic}",
                answer=generate_random_string(20),
                correct=random.choice([True, False]),
                feedback="Good job!" if random.random() > 0.5 else "Try again."
            ))
            assessments.append(assessment)
    
    return assessments

def create_test_quantum_states(db: Session, users: List[User]) -> List[QuantumState]:
    """Create test quantum states."""
    states = []
    quantum_service = QuantumService(db)
    
    for user in users:
        for i in range(2):
            state = quantum_service.create_quantum_state(QuantumStateCreate(
                user_id=user.id,
                state_vector=f"[{random.random()}, {random.random()}, {random.random()}]"
            ))
            states.append(state)
    
    return states

def create_test_feedback(db: Session, content: List[Content], users: List[User]) -> List[Feedback]:
    """Create test feedback."""
    feedbacks = []
    feedback_service = FeedbackService(db)
    
    for content_item in content:
        for user in users:
            feedback = feedback_service.create_feedback(FeedbackCreate(
                content_id=content_item.id,
                user_id=user.id,
                rating=random.randint(1, 5),
                comment=f"Great {content_item.content_type}! {generate_random_string(30)}"
            ))
            feedbacks.append(feedback)
    
    return feedbacks

def main():
    # Initialize database
    init_db()
    db = next(get_db())
    
    print("Creating test data...")
    
    # Create users
    print("Creating users...")
    users = create_test_users(db)
    
    # Create profiles
    print("Creating profiles...")
    profiles = create_test_profiles(db, users)
    
    # Create sessions
    print("Creating sessions...")
    sessions = create_test_sessions(db, users)
    
    # Create content
    print("Creating content...")
    content = create_test_content(db, sessions)
    
    # Create assessments
    print("Creating assessments...")
    assessments = create_test_assessments(db, sessions)
    
    # Create quantum states
    print("Creating quantum states...")
    quantum_states = create_test_quantum_states(db, users)
    
    # Create feedback
    print("Creating feedback...")
    feedbacks = create_test_feedback(db, content, users)
    
    print("\nTest data creation complete!")
    print(f"Created {len(users)} users")
    print(f"Created {len(profiles)} profiles")
    print(f"Created {len(sessions)} sessions")
    print(f"Created {len(content)} content items")
    print(f"Created {len(assessments)} assessments")
    print(f"Created {len(quantum_states)} quantum states")
    print(f"Created {len(feedbacks)} feedback items")

if __name__ == "__main__":
    main()
