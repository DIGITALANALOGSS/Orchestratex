import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import numpy as np
from scipy.stats import norm
from enum import Enum

class ChallengeType(Enum):
    """Types of challenges."""
    CODING = "coding"
    DESIGN = "design"
    CREATIVE = "creative"
    COLLABORATION = "collaboration"
    LEARNING = "learning"
    INNOVATION = "innovation"

class BadgeType(Enum):
    """Types of badges."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    MASTER = "master"
    LEGEND = "legend"

class GamificationManager:
    def __init__(self):
        """Initialize the gamification manager."""
        self.logger = logging.getLogger(__name__)
        self.user_progress = {}
        self.challenges = {}
        self.badges = {}
        self.leaderboard = {}
        self.load_data()
        
    def load_data(self):
        """Load gamification data from files."""
        try:
            # Load challenges
            with open('data/challenges.json', 'r') as f:
                self.challenges = json.load(f)
            
            # Load badges
            with open('data/badges.json', 'r') as f:
                self.badges = json.load(f)
            
            # Load user progress
            with open('data/user_progress.json', 'r') as f:
                self.user_progress = json.load(f)
            
            # Load leaderboard
            with open('data/leaderboard.json', 'r') as f:
                self.leaderboard = json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load gamification data: {str(e)}")
            self._initialize_default_data()
            
    def _initialize_default_data(self):
        """Initialize default gamification data."""
        self.challenges = {
            "welcome": {
                "type": ChallengeType.CREATIVE,
                "title": "Welcome to Orchestratex",
                "description": "Complete the onboarding tutorial",
                "points": 100,
                "difficulty": "easy"
            },
            "first_project": {
                "type": ChallengeType.CODING,
                "title": "Create Your First Project",
                "description": "Build a simple quantum circuit",
                "points": 200,
                "difficulty": "medium"
            }
        }
        
        self.badges = {
            "beginner": {
                "type": BadgeType.BEGINNER,
                "title": "Quantum Explorer",
                "description": "Completed the onboarding",
                "requirements": {"points": 100}
            },
            "intermediate": {
                "type": BadgeType.INTERMEDIATE,
                "title": "Quantum Engineer",
                "description": "Created first quantum circuit",
                "requirements": {"points": 500}
            }
        }
        
        self.user_progress = {}
        self.leaderboard = {}
        
    def create_challenge(self, challenge_type: ChallengeType, title: str, description: str, points: int, difficulty: str) -> str:
        """Create a new challenge.
        
        Args:
            challenge_type: Type of challenge
            title: Challenge title
            description: Challenge description
            points: Points awarded
            difficulty: Difficulty level
            
        Returns:
            Challenge ID
        """
        challenge_id = f"challenge_{str(uuid.uuid4())[:8]}"
        self.challenges[challenge_id] = {
            "type": challenge_type.value,
            "title": title,
            "description": description,
            "points": points,
            "difficulty": difficulty,
            "created_at": datetime.now().isoformat()
        }
        self._save_data()
        return challenge_id
        
    def get_random_challenge(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a random challenge for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Random challenge or None if none available
        """
        try:
            # Get user's current progress
            progress = self.user_progress.get(user_id, {})
            completed = progress.get("completed_challenges", [])
            
            # Filter out completed challenges
            available_challenges = {
                cid: c for cid, c in self.challenges.items()
                if cid not in completed
            }
            
            if not available_challenges:
                return None
                
            # Select challenge based on user's level
            user_level = self._get_user_level(user_id)
            
            # Calculate challenge weights based on difficulty
            weights = {}
            for cid, challenge in available_challenges.items():
                diff = challenge["difficulty"]
                weight = 1.0
                
                if diff == "easy":
                    weight *= 0.8
                elif diff == "medium":
                    weight *= 1.0
                else:  # hard
                    weight *= 1.2
                    
                weights[cid] = weight
                
            # Normalize weights
            total_weight = sum(weights.values())
            normalized_weights = {
                cid: w / total_weight
                for cid, w in weights.items()
            }
            
            # Select challenge using weighted random choice
            choices = list(normalized_weights.keys())
            probabilities = list(normalized_weights.values())
            selected_cid = np.random.choice(choices, p=probabilities)
            
            return available_challenges[selected_cid]
            
        except Exception as e:
            self.logger.error(f"Failed to get random challenge: {str(e)}")
            return None
            
    def complete_challenge(self, user_id: str, challenge_id: str) -> bool:
        """Mark a challenge as completed.
        
        Args:
            user_id: User ID
            challenge_id: Challenge ID
            
        Returns:
            True if challenge completed successfully, False otherwise
        """
        try:
            if challenge_id not in self.challenges:
                return False
                
            challenge = self.challenges[challenge_id]
            user_progress = self.user_progress.setdefault(user_id, {
                "completed_challenges": [],
                "points": 0,
                "badges": [],
                "last_activity": datetime.now().isoformat()
            })
            
            if challenge_id in user_progress["completed_challenges"]:
                return False
                
            # Update user progress
            user_progress["completed_challenges"].append(challenge_id)
            user_progress["points"] += challenge["points"]
            user_progress["last_activity"] = datetime.now().isoformat()
            
            # Check for new badges
            self._check_badges(user_id)
            
            # Update leaderboard
            self._update_leaderboard(user_id)
            
            self._save_data()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete challenge: {str(e)}")
            return False
            
    def _check_badges(self, user_id: str):
        """Check if user qualifies for new badges.
        
        Args:
            user_id: User ID
        """
        try:
            user_progress = self.user_progress.get(user_id, {})
            points = user_progress.get("points", 0)
            
            for badge_id, badge in self.badges.items():
                if badge_id not in user_progress.get("badges", []) and \
                   points >= badge["requirements"]["points"]:
                    user_progress["badges"].append(badge_id)
                    self.logger.info(f"User {user_id} earned badge: {badge['title']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to check badges: {str(e)}")
            
    def _update_leaderboard(self, user_id: str):
        """Update the leaderboard.
        
        Args:
            user_id: User ID
        """
        try:
            user_progress = self.user_progress.get(user_id, {})
            points = user_progress.get("points", 0)
            
            self.leaderboard[user_id] = {
                "points": points,
                "badges": len(user_progress.get("badges", [])),
                "completed_challenges": len(user_progress.get("completed_challenges", []))
            }
            
            # Sort leaderboard by points
            self.leaderboard = dict(sorted(
                self.leaderboard.items(),
                key=lambda x: x[1]["points"],
                reverse=True
            ))
            
        except Exception as e:
            self.logger.error(f"Failed to update leaderboard: {str(e)}")
            
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the top users from the leaderboard.
        
        Args:
            limit: Number of users to return
            
        Returns:
            List of top users
        """
        try:
            return [
                {
                    "user_id": user_id,
                    "points": stats["points"],
                    "badges": stats["badges"],
                    "completed_challenges": stats["completed_challenges"]
                }
                for user_id, stats in list(self.leaderboard.items())[:limit]
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {str(e)}")
            return []
            
    def _save_data(self):
        """Save gamification data to files."""
        try:
            with open('data/challenges.json', 'w') as f:
                json.dump(self.challenges, f, indent=2)
            
            with open('data/badges.json', 'w') as f:
                json.dump(self.badges, f, indent=2)
            
            with open('data/user_progress.json', 'w') as f:
                json.dump(self.user_progress, f, indent=2)
            
            with open('data/leaderboard.json', 'w') as f:
                json.dump(self.leaderboard, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save gamification data: {str(e)}")
            raise
            
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's gamification statistics.
        
        Args:
            user_id: User ID
            
        Returns:
            User statistics
        """
        try:
            progress = self.user_progress.get(user_id, {
                "completed_challenges": [],
                "points": 0,
                "badges": [],
                "last_activity": datetime.now().isoformat()
            })
            
            return {
                "points": progress["points"],
                "badges": len(progress["badges"]),
                "completed_challenges": len(progress["completed_challenges"]),
                "last_activity": progress["last_activity"],
                "rank": self._get_user_rank(user_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {str(e)}")
            return {
                "points": 0,
                "badges": 0,
                "completed_challenges": 0,
                "last_activity": datetime.now().isoformat(),
                "rank": -1
            }
            
    def _get_user_rank(self, user_id: str) -> int:
        """Get user's rank on the leaderboard.
        
        Args:
            user_id: User ID
            
        Returns:
            User's rank (1-based)
        """
        try:
            if user_id not in self.leaderboard:
                return -1
                
            sorted_users = list(self.leaderboard.keys())
            return sorted_users.index(user_id) + 1
            
        except Exception as e:
            self.logger.error(f"Failed to get user rank: {str(e)}")
            return -1
