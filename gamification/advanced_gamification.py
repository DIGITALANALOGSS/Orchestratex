import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
import numpy as np
from scipy.stats import norm
from enum import Enum
import uuid

class ChallengeDifficulty(Enum):
    """Challenge difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class RewardType(Enum):
    """Types of rewards."""
    POINTS = "points"
    BADGE = "badge"
    BOOST = "boost"
    ITEM = "item"

class AdvancedGamification:
    def __init__(self):
        """Initialize advanced gamification system."""
        self.logger = logging.getLogger(__name__)
        self.challenges = {}
        self.rewards = {}
        self.user_progress = {}
        self.load_data()
        
    def load_data(self):
        """Load gamification data from files."""
        try:
            # Load challenges
            with open('data/challenges.json', 'r') as f:
                self.challenges = json.load(f)
            
            # Load rewards
            with open('data/rewards.json', 'r') as f:
                self.rewards = json.load(f)
            
            # Load user progress
            with open('data/user_progress.json', 'r') as f:
                self.user_progress = json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load gamification data: {str(e)}")
            self._initialize_default_data()
            
    def _initialize_default_data(self):
        """Initialize default gamification data."""
        self.challenges = {
            "quantum_basics": {
                "type": "quantum",
                "difficulty": ChallengeDifficulty.BEGINNER,
                "title": "Quantum Basics",
                "description": "Complete quantum circuit tutorial",
                "points": 100,
                "requirements": {"completed": 0},
                "reward": "quantum_badge"
            },
            "advanced_circuits": {
                "type": "quantum",
                "difficulty": ChallengeDifficulty.ADVANCED,
                "title": "Advanced Circuits",
                "description": "Design complex quantum circuits",
                "points": 500,
                "requirements": {"completed": 5},
                "reward": "advanced_badge"
            }
        }
        
        self.rewards = {
            "quantum_badge": {
                "type": RewardType.BADGE,
                "title": "Quantum Explorer",
                "description": "Completed quantum basics",
                "points": 100
            },
            "advanced_badge": {
                "type": RewardType.BADGE,
                "title": "Quantum Engineer",
                "description": "Mastered advanced circuits",
                "points": 500
            }
        }
        
        self.user_progress = {}
        
    def create_dynamic_challenge(self, user_id: str) -> Dict[str, Any]:
        """Create a dynamic challenge based on user progress.
        
        Args:
            user_id: User ID
            
        Returns:
            Challenge dictionary
        """
        try:
            # Get user's current level
            progress = self.user_progress.get(user_id, {})
            points = progress.get("points", 0)
            
            # Determine appropriate difficulty
            if points < 100:
                difficulty = ChallengeDifficulty.BEGINNER
            elif points < 500:
                difficulty = ChallengeDifficulty.INTERMEDIATE
            elif points < 1000:
                difficulty = ChallengeDifficulty.ADVANCED
            else:
                difficulty = ChallengeDifficulty.EXPERT
                
            # Generate challenge parameters
            challenge_id = f"challenge_{str(uuid.uuid4())[:8]}"
            
            challenge = {
                "id": challenge_id,
                "type": "quantum",
                "difficulty": difficulty.value,
                "title": f"Quantum Challenge {difficulty.value.title()}",
                "description": f"Solve quantum problems at {difficulty.value} level",
                "points": self._calculate_points(difficulty),
                "requirements": self._generate_requirements(difficulty),
                "reward": self._select_reward(difficulty),
                "created_at": datetime.now().isoformat()
            }
            
            self.challenges[challenge_id] = challenge
            self._save_data()
            
            return challenge
            
        except Exception as e:
            self.logger.error(f"Failed to create challenge: {str(e)}")
            raise
            
    def _calculate_points(self, difficulty: ChallengeDifficulty) -> int:
        """Calculate points based on difficulty.
        
        Args:
            difficulty: Challenge difficulty
            
        Returns:
            Points value
        """
        base_points = {
            ChallengeDifficulty.BEGINNER: 100,
            ChallengeDifficulty.INTERMEDIATE: 200,
            ChallengeDifficulty.ADVANCED: 500,
            ChallengeDifficulty.EXPERT: 1000
        }
        
        return base_points[difficulty] + random.randint(-20, 20)
        
    def _generate_requirements(self, difficulty: ChallengeDifficulty) -> Dict[str, Any]:
        """Generate challenge requirements.
        
        Args:
            difficulty: Challenge difficulty
            
        Returns:
            Requirements dictionary
        """
        requirements = {
            "completed": 0,
            "time_limit": 3600,  # 1 hour in seconds
            "accuracy": 0.8
        }
        
        if difficulty == ChallengeDifficulty.BEGINNER:
            requirements["completed"] = 1
        elif difficulty == ChallengeDifficulty.INTERMEDIATE:
            requirements["completed"] = 3
            requirements["accuracy"] = 0.9
        elif difficulty == ChallengeDifficulty.ADVANCED:
            requirements["completed"] = 5
            requirements["accuracy"] = 0.95
        else:  # EXPERT
            requirements["completed"] = 10
            requirements["accuracy"] = 0.98
            
        return requirements
        
    def _select_reward(self, difficulty: ChallengeDifficulty) -> str:
        """Select appropriate reward.
        
        Args:
            difficulty: Challenge difficulty
            
        Returns:
            Reward ID
        """
        rewards = {
            ChallengeDifficulty.BEGINNER: "quantum_badge",
            ChallengeDifficulty.INTERMEDIATE: "advanced_badge",
            ChallengeDifficulty.ADVANCED: "expert_badge",
            ChallengeDifficulty.EXPERT: "master_badge"
        }
        
        return rewards[difficulty]
        
    def complete_challenge(self, user_id: str, challenge_id: str, accuracy: float) -> bool:
        """Mark a challenge as completed.
        
        Args:
            user_id: User ID
            challenge_id: Challenge ID
            accuracy: Completion accuracy
            
        Returns:
            True if challenge completed successfully, False otherwise
        """
        try:
            if challenge_id not in self.challenges:
                return False
                
            challenge = self.challenges[challenge_id]
            requirements = challenge["requirements"]
            
            if accuracy < requirements["accuracy"]:
                return False
                
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
            
            # Award reward
            self._award_reward(user_id, challenge["reward"])
            
            self._save_data()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete challenge: {str(e)}")
            return False
            
    def _award_reward(self, user_id: str, reward_id: str):
        """Award a reward to a user.
        
        Args:
            user_id: User ID
            reward_id: Reward ID
        """
        try:
            user_progress = self.user_progress.get(user_id, {})
            rewards = user_progress.setdefault("rewards", [])
            
            if reward_id not in rewards:
                rewards.append(reward_id)
                reward = self.rewards.get(reward_id)
                if reward:
                    user_progress["points"] += reward.get("points", 0)
                    self.logger.info(f"User {user_id} earned reward: {reward['title']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to award reward: {str(e)}")
            
    def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the top users from the leaderboard.
        
        Args:
            limit: Number of users to return
            
        Returns:
            List of top users
        """
        try:
            # Calculate user scores
            scores = []
            for user_id, progress in self.user_progress.items():
                score = {
                    "user_id": user_id,
                    "points": progress.get("points", 0),
                    "completed_challenges": len(progress.get("completed_challenges", [])),
                    "badges": len(progress.get("badges", [])),
                    "rewards": len(progress.get("rewards", []))
                }
                scores.append(score)
                
            # Sort by points
            scores.sort(key=lambda x: x["points"], reverse=True)
            
            return scores[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get leaderboard: {str(e)}")
            return []
            
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
                "rewards": [],
                "last_activity": datetime.now().isoformat()
            })
            
            return {
                "points": progress["points"],
                "completed_challenges": len(progress["completed_challenges"]),
                "badges": len(progress["badges"]),
                "rewards": len(progress["rewards"]),
                "last_activity": progress["last_activity"],
                "rank": self._get_user_rank(user_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user stats: {str(e)}")
            return {
                "points": 0,
                "completed_challenges": 0,
                "badges": 0,
                "rewards": 0,
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
            if user_id not in self.user_progress:
                return -1
                
            # Calculate scores
            scores = []
            for uid, progress in self.user_progress.items():
                scores.append((uid, progress.get("points", 0)))
                
            # Sort scores
            scores.sort(key=lambda x: x[1], reverse=True)
            
            # Find user's rank
            for i, (uid, _) in enumerate(scores):
                if uid == user_id:
                    return i + 1
                    
            return -1
            
        except Exception as e:
            self.logger.error(f"Failed to get user rank: {str(e)}")
            return -1
            
    def _save_data(self):
        """Save gamification data to files."""
        try:
            with open('data/challenges.json', 'w') as f:
                json.dump(self.challenges, f, indent=2)
            
            with open('data/rewards.json', 'w') as f:
                json.dump(self.rewards, f, indent=2)
            
            with open('data/user_progress.json', 'w') as f:
                json.dump(self.user_progress, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save gamification data: {str(e)}")
            raise
