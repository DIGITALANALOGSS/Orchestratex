from .base import AgentBase

class MentorAgent(AgentBase):
    def __init__(self, name="MentorAgent"):
        super().__init__(name, "Personal Learning Mentor")
    
    def analyze_user(self, profile):
        return f"Analysis for {profile.get('user_id', 'unknown')}: Strengths - {profile.get('strengths', [])}, Gaps - {profile.get('gaps', [])}"
    
    def recommend_next(self, progress):
        return f"Next recommended lesson: {progress.get('next_topic', 'N/A')}"
    
    def encourage(self, user_id):
        return f"Keep going, {user_id}! Every step is progress."
    
    def feedback(self, user_id, result):
        return f"{user_id}, here's how you can improve: {result.get('suggestion', 'Keep practicing!')}"
