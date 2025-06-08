from .base import AgentBase
from collections import defaultdict

class GamificationAgent(AgentBase):
    def __init__(self, name="GamificationAgent"):
        super().__init__(name, "Engagement & Motivation")
        self.badges = defaultdict(list)
        self.progress = defaultdict(dict)
        self.leaderboard = []
    
    def award_badge(self, user_id, badge):
        self.badges[user_id].append(badge)
        return f"Awarded {badge} to {user_id}"
    
    def track_progress(self, user_id, lesson):
        self.progress[user_id][lesson] = self.progress[user_id].get(lesson, 0) + 1
        return f"{user_id} completed {lesson}"
    
    def leaderboard(self):
        self.update_leaderboard()
        return f"Leaderboard: {self.leaderboard[:5]}"  # Top 5 users
    
    def celebrate(self, user_id):
        return f"\U0001F389 Congratulations, {user_id}! New achievement unlocked!"
    
    def update_leaderboard(self):
        scores = []
        for user_id, lessons in self.progress.items():
            score = sum(lessons.values()) + len(self.badges[user_id]) * 2
            scores.append((user_id, score))
        self.leaderboard = sorted(scores, key=lambda x: x[1], reverse=True)
    
    def get_user_stats(self, user_id):
        return {
            "completed_lessons": len(self.progress[user_id]),
            "badges": len(self.badges[user_id]),
            "score": sum(self.progress[user_id].values()) + len(self.badges[user_id]) * 2
        }
