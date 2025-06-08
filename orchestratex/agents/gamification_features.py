from typing import Dict, List, Tuple, Any
from datetime import datetime

class GamificationFeatures:
    """Additional gamification features for the GamificationAgent."""
    
    def __init__(self, agent: 'GamificationAgent'):
        self.agent = agent
        self.achievements: Dict[str, List[Dict[str, Any]]] = {}
        self.challenges: Dict[str, Dict[str, Any]] = {}
        self.leaderboards: Dict[str, Dict[str, Any]] = {}
        
    def unlock_achievement(self, user_id: str, achievement: Dict[str, Any]) -> Tuple[bool, str]:
        """Unlock an achievement for a user."""
        try:
            # Verify user access
            if not self.agent._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Encrypt achievement
            encrypted_achievement = self.agent._encrypt_badge(achievement)
            
            # Store achievement
            if user_id not in self.achievements:
                self.achievements[user_id] = []
                self.agent.metrics["users_engaged"] += 1
            
            self.achievements[user_id].append({
                "achievement": encrypted_achievement,
                "timestamp": datetime.now().isoformat(),
                "metadata": achievement.get("metadata", {})
            })
            
            # Update metrics
            self.agent.metrics["achievements_unlocked"] += 1
            self.agent.metrics["security_checks"] += 1
            
            # Update leaderboard
            self.agent._update_leaderboard(user_id, achievement["points"])
            
            # Log audit entry
            self.agent._audit(f"Achievement unlocked for {user_id}", "engagement")
            
            return True, "Achievement unlocked successfully"
            
        except Exception as e:
            self.agent.logger.error(f"Failed to unlock achievement: {str(e)}")
            self.agent.metrics["errors"] += 1
            return False, f"Failed to unlock achievement: {str(e)}"

    def get_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's achievements."""
        try:
            # Verify user access
            if not self.agent._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Get achievements
            achievements = self.achievements.get(user_id, [])
            
            # Decrypt achievements
            decrypted_achievements = []
            for achievement in achievements:
                decrypted_achievement = self.agent._decrypt_badge(achievement["achievement"])
                decrypted_achievements.append({
                    "achievement": decrypted_achievement,
                    "timestamp": achievement["timestamp"],
                    "metadata": achievement["metadata"]
                })
                
            # Update metrics
            self.agent.metrics["security_checks"] += 1
            
            # Log audit entry
            self.agent._audit(f"Achievements retrieved for {user_id}", "engagement")
            
            return decrypted_achievements
            
        except Exception as e:
            self.agent.logger.error(f"Failed to get achievements: {str(e)}")
            self.agent.metrics["errors"] += 1
            raise

    def start_challenge(self, user_id: str, challenge_id: str) -> Tuple[bool, str]:
        """Start a challenge for a user."""
        try:
            # Verify user access
            if not self.agent._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Get challenge
            challenge = self.agent.challenges.get(challenge_id)
            if not challenge:
                raise ValueError(f"Challenge {challenge_id} not found")
                
            # Check deadline
            if datetime.now() > challenge["deadline"]:
                raise ValueError("Challenge deadline has passed")
                
            # Store challenge progress
            if user_id not in self.challenges:
                self.challenges[user_id] = {}
            
            self.challenges[user_id][challenge_id] = {
                "started_at": datetime.now().isoformat(),
                "status": "in_progress",
                "progress": 0,
                "requirements": challenge["requirements"]
            }
            
            # Update metrics
            self.agent.metrics["security_checks"] += 1
            
            # Log audit entry
            self.agent._audit(f"Challenge started by {user_id}: {challenge_id}", "engagement")
            
            return True, "Challenge started successfully"
            
        except Exception as e:
            self.agent.logger.error(f"Failed to start challenge: {str(e)}")
            self.agent.metrics["errors"] += 1
            return False, f"Failed to start challenge: {str(e)}"

    def get_leaderboard(self, category: str = "overall") -> List[Dict[str, Any]]:
        """Get leaderboard."""
        try:
            # Get leaderboard
            leaderboard = self.leaderboards.get(category, [])
            
            # Sort by points
            sorted_leaderboard = sorted(
                leaderboard,
                key=lambda x: x["points"],
                reverse=True
            )
            
            # Update metrics
            self.agent.metrics["leaderboard_updates"] += 1
            
            # Log audit entry
            self.agent._audit(f"Leaderboard retrieved: {category}", "engagement")
            
            return sorted_leaderboard
            
        except Exception as e:
            self.agent.logger.error(f"Failed to get leaderboard: {str(e)}")
            self.agent.metrics["errors"] += 1
            raise

    def get_user_rank(self, user_id: str) -> Tuple[int, int]:
        """Get user's rank in the leaderboard."""
        try:
            # Get leaderboard
            leaderboard = self.leaderboards.get("overall", [])
            
            # Find user position
            rank = -1
            total_users = len(leaderboard)
            
            for i, entry in enumerate(leaderboard):
                if entry["user_id"] == user_id:
                    rank = i + 1
                    break
                    
            # Update metrics
            self.agent.metrics["security_checks"] += 1
            
            # Log audit entry
            self.agent._audit(f"User rank retrieved for {user_id}", "engagement")
            
            return rank, total_users
            
        except Exception as e:
            self.agent.logger.error(f"Failed to get user rank: {str(e)}")
            self.agent.metrics["errors"] += 1
            raise
