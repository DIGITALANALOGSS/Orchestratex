import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random
from enum import Enum
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class LearningPathType(Enum):
    """Types of learning paths."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class LearningManager:
    def __init__(self):
        """Initialize the learning manager."""
        self.logger = logging.getLogger(__name__)
        self.learning_paths = {}
        self.user_progress = {}
        self.content_library = {}
        self.load_data()
        
    def load_data(self):
        """Load learning data from files."""
        try:
            # Load learning paths
            with open('data/learning_paths.json', 'r') as f:
                self.learning_paths = json.load(f)
            
            # Load content library
            with open('data/content_library.json', 'r') as f:
                self.content_library = json.load(f)
            
            # Load user progress
            with open('data/user_progress.json', 'r') as f:
                self.user_progress = json.load(f)
                
        except Exception as e:
            self.logger.error(f"Failed to load learning data: {str(e)}")
            self._initialize_default_data()
            
    def _initialize_default_data(self):
        """Initialize default learning data."""
        self.learning_paths = {
            "quantum_basics": {
                "type": LearningPathType.BEGINNER,
                "title": "Quantum Computing Fundamentals",
                "description": "Learn the basics of quantum computing",
                "modules": [
                    "quantum_basics_1",
                    "quantum_basics_2",
                    "quantum_basics_3"
                ]
            },
            "quantum_algorithms": {
                "type": LearningPathType.INTERMEDIATE,
                "title": "Quantum Algorithms",
                "description": "Learn quantum algorithms and their applications",
                "modules": [
                    "quantum_algorithms_1",
                    "quantum_algorithms_2",
                    "quantum_algorithms_3"
                ]
            }
        }
        
        self.content_library = {
            "quantum_basics_1": {
                "title": "Introduction to Quantum Computing",
                "type": "video",
                "duration": "30:00",
                "difficulty": "beginner",
                "topics": ["quantum_bits", "superposition", "entanglement"]
            },
            "quantum_algorithms_1": {
                "title": "Quantum Search Algorithms",
                "type": "interactive",
                "duration": "45:00",
                "difficulty": "intermediate",
                "topics": ["grover_search", "quantum_oracles", "amplitude_amplification"]
            }
        }
        
        self.user_progress = {}
        
    def create_learning_path(self, path_type: LearningPathType, title: str, description: str, modules: List[str]) -> str:
        """Create a new learning path.
        
        Args:
            path_type: Type of learning path
            title: Path title
            description: Path description
            modules: List of module IDs
            
        Returns:
            Learning path ID
        """
        path_id = f"path_{str(uuid.uuid4())[:8]}"
        self.learning_paths[path_id] = {
            "type": path_type.value,
            "title": title,
            "description": description,
            "modules": modules,
            "created_at": datetime.now().isoformat()
        }
        self._save_data()
        return path_id
        
    def recommend_learning_path(self, user_id: str, interests: List[str]) -> Optional[str]:
        """Recommend a learning path based on user interests.
        
        Args:
            user_id: User ID
            interests: List of user interests
            
        Returns:
            Recommended learning path ID or None if none found
        """
        try:
            # Get user's current progress
            progress = self.user_progress.get(user_id, {})
            completed_paths = progress.get("completed_paths", [])
            
            # Vectorize interests
            vectorizer = TfidfVectorizer()
            interest_vector = vectorizer.fit_transform([" ".join(interests)])
            
            # Calculate similarity scores for each path
            scores = {}
            for path_id, path in self.learning_paths.items():
                if path_id in completed_paths:
                    continue
                    
                # Get path topics
                topics = []
                for module_id in path["modules"]:
                    module = self.content_library.get(module_id)
                    if module:
                        topics.extend(module.get("topics", []))
                
                if not topics:
                    continue
                    
                # Calculate similarity
                path_vector = vectorizer.transform([" ".join(topics)])
                score = cosine_similarity(interest_vector, path_vector)[0][0]
                scores[path_id] = score
                
            # Select path with highest score
            if not scores:
                return None
                
            recommended_path = max(scores.items(), key=lambda x: x[1])[0]
            return recommended_path
            
        except Exception as e:
            self.logger.error(f"Failed to recommend learning path: {str(e)}")
            return None
            
    def get_learning_path(self, path_id: str) -> Optional[Dict[str, Any]]:
        """Get a learning path by ID.
        
        Args:
            path_id: Learning path ID
            
        Returns:
            Learning path information or None if not found
        """
        return self.learning_paths.get(path_id)
        
    def get_module_content(self, module_id: str) -> Optional[Dict[str, Any]]:
        """Get module content by ID.
        
        Args:
            module_id: Module ID
            
        Returns:
            Module content or None if not found
        """
        return self.content_library.get(module_id)
        
    def complete_module(self, user_id: str, module_id: str) -> bool:
        """Mark a module as completed.
        
        Args:
            user_id: User ID
            module_id: Module ID
            
        Returns:
            True if module completed successfully, False otherwise
        """
        try:
            if module_id not in self.content_library:
                return False
                
            user_progress = self.user_progress.setdefault(user_id, {
                "completed_modules": [],
                "completed_paths": [],
                "points": 0,
                "last_activity": datetime.now().isoformat()
            })
            
            if module_id in user_progress["completed_modules"]:
                return False
                
            # Update user progress
            user_progress["completed_modules"].append(module_id)
            user_progress["points"] += self._get_module_points(module_id)
            user_progress["last_activity"] = datetime.now().isoformat()
            
            # Check if path is completed
            self._check_path_completion(user_id)
            
            self._save_data()
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to complete module: {str(e)}")
            return False
            
    def _get_module_points(self, module_id: str) -> int:
        """Get points for completing a module.
        
        Args:
            module_id: Module ID
            
        Returns:
            Points for module completion
        """
        try:
            module = self.content_library.get(module_id)
            if not module:
                return 0
                
            difficulty = module.get("difficulty", "beginner")
            points = 100
            
            if difficulty == "intermediate":
                points = 200
            elif difficulty == "advanced":
                points = 300
            elif difficulty == "expert":
                points = 500
                
            return points
            
        except Exception as e:
            self.logger.error(f"Failed to get module points: {str(e)}")
            return 0
            
    def _check_path_completion(self, user_id: str):
        """Check if user has completed any learning paths.
        
        Args:
            user_id: User ID
        """
        try:
            user_progress = self.user_progress.get(user_id, {})
            completed_modules = set(user_progress.get("completed_modules", []))
            
            for path_id, path in self.learning_paths.items():
                if path_id in user_progress.get("completed_paths", []):
                    continue
                    
                required_modules = set(path["modules"])
                if required_modules.issubset(completed_modules):
                    user_progress["completed_paths"].append(path_id)
                    user_progress["points"] += 500  # Bonus for completing path
                    self.logger.info(f"User {user_id} completed learning path: {path['title']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to check path completion: {str(e)}")
            
    def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning progress.
        
        Args:
            user_id: User ID
            
        Returns:
            User's learning progress
        """
        try:
            progress = self.user_progress.get(user_id, {
                "completed_modules": [],
                "completed_paths": [],
                "points": 0,
                "last_activity": datetime.now().isoformat()
            })
            
            return {
                "points": progress["points"],
                "completed_modules": len(progress["completed_modules"]),
                "completed_paths": len(progress["completed_paths"]),
                "last_activity": progress["last_activity"],
                "progress_percentage": self._calculate_progress_percentage(user_id)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get user progress: {str(e)}")
            return {
                "points": 0,
                "completed_modules": 0,
                "completed_paths": 0,
                "last_activity": datetime.now().isoformat(),
                "progress_percentage": 0
            }
            
    def _calculate_progress_percentage(self, user_id: str) -> float:
        """Calculate user's overall progress percentage.
        
        Args:
            user_id: User ID
            
        Returns:
            Progress percentage (0-100)
        """
        try:
            progress = self.user_progress.get(user_id, {})
            completed_modules = set(progress.get("completed_modules", []))
            
            total_modules = len(self.content_library)
            if total_modules == 0:
                return 0
                
            return (len(completed_modules) / total_modules) * 100
            
        except Exception as e:
            self.logger.error(f"Failed to calculate progress percentage: {str(e)}")
            return 0
            
    def _save_data(self):
        """Save learning data to files."""
        try:
            with open('data/learning_paths.json', 'w') as f:
                json.dump(self.learning_paths, f, indent=2)
            
            with open('data/content_library.json', 'w') as f:
                json.dump(self.content_library, f, indent=2)
            
            with open('data/user_progress.json', 'w') as f:
                json.dump(self.user_progress, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {str(e)}")
            raise
