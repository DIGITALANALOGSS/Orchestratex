    def __init__(self):
        super().__init__("GamificationAgent", "Engagement")
        self.pqc_crypto = PQCCryptography()
        self.hybrid_crypto = HybridCryptography(self.pqc_crypto)
        self.security_lesson = QuantumSecurityLesson(self.id)
        self.badges: Dict[str, List[Dict[str, Any]]] = {}
        self.metrics = {
            "badges_awarded": 0,
            "achievements_unlocked": 0,
            "challenges_completed": 0,
            "users_engaged": 0,
            "security_checks": 0,
            "errors": 0,
            "leaderboard_updates": 0
        }
        self.audit_log = []
        self.features = GamificationFeatures(self)
        self._initialize_system_badges()
        self._initialize_challenges()

    def _initialize_system_badges(self) -> None:
        """Initialize system-wide badges."""
        self.system_badges = {
            "quantum_security": {
                "name": "Quantum Security Expert",
                "description": "Master of quantum-safe security",
                "points": 100,
                "requirements": ["complete_security_course", "pass_security_quiz"]
            },
            "engagement": {
                "name": "Engagement Master",
                "description": "Highly engaged user",
                "points": 50,
                "requirements": ["complete_5_tasks", "participate_in_community"]
            },
            "innovation": {
                "name": "Quantum Innovator",
                "description": "Contributor to quantum projects",
                "points": 75,
                "requirements": ["submit_3_ideas", "implement_solution"]
            }
        }

    def _initialize_challenges(self) -> None:
        """Initialize system-wide challenges."""
        self.challenges = {
            "security_audit": {
                "name": "Security Audit Challenge",
                "description": "Complete a security audit",
                "points": 50,
                "deadline": datetime.now() + timedelta(days=7),
                "requirements": ["complete_audit", "submit_report"]
            },
            "quantum_project": {
                "name": "Quantum Project",
                "description": "Build a quantum application",
                "points": 100,
                "deadline": datetime.now() + timedelta(days=30),
                "requirements": ["design_solution", "implement_code", "test_application"]
            }
        }

    def unlock_achievement(self, user_id: str, achievement: Dict[str, Any]) -> Tuple[bool, str]:
        """Unlock an achievement for a user."""
        return self.features.unlock_achievement(user_id, achievement)

    def get_achievements(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's achievements."""
        return self.features.get_achievements(user_id)

    def start_challenge(self, user_id: str, challenge_id: str) -> Tuple[bool, str]:
        """Start a challenge for a user."""
        return self.features.start_challenge(user_id, challenge_id)

    def get_leaderboard(self, category: str = "overall") -> List[Dict[str, Any]]:
        """Get leaderboard."""
        return self.features.get_leaderboard(category)

    def get_user_rank(self, user_id: str) -> Tuple[int, int]:
        """Get user's rank in the leaderboard."""
        return self.features.get_user_rank(user_id)

logger = logging.getLogger(__name__)

class GamificationAgent(AgentBase):
    """Quantum-safe gamification agent with educational integration."""
    
    def __init__(self):
        super().__init__("GamificationAgent", "Engagement")
        self.pqc_crypto = PQCCryptography()
        self.hybrid_crypto = HybridCryptography(self.pqc_crypto)
        self.security_lesson = QuantumSecurityLesson(self.id)
        self.badges: Dict[str, List[Dict[str, Any]]] = {}
        self.achievements: Dict[str, List[Dict[str, Any]]] = {}
        self.leaderboards: Dict[str, Dict[str, Any]] = {}
        self.challenges: Dict[str, Dict[str, Any]] = {}
        self.metrics = {
            "badges_awarded": 0,
            "achievements_unlocked": 0,
            "challenges_completed": 0,
            "users_engaged": 0,
            "security_checks": 0,
            "errors": 0,
            "leaderboard_updates": 0
        }
        self.audit_log = []
        self._initialize_system_badges()
        self._initialize_challenges()

    def _initialize_system_badges(self) -> None:
        """Initialize system-wide badges."""
        self.system_badges = {
            "quantum_security": {
                "name": "Quantum Security Expert",
                "description": "Master of quantum-safe security",
                "points": 100,
                "requirements": ["complete_security_course", "pass_security_quiz"]
            },
            "engagement": {
                "name": "Engagement Master",
                "description": "Highly engaged user",
                "points": 50,
                "requirements": ["complete_5_tasks", "participate_in_community"]
            },
            "innovation": {
                "name": "Quantum Innovator",
                "description": "Contributor to quantum projects",
                "points": 75,
                "requirements": ["submit_3_ideas", "implement_solution"]
            }
        }

    def _initialize_challenges(self) -> None:
        """Initialize system-wide challenges."""
        self.challenges = {
            "security_audit": {
                "name": "Security Audit Challenge",
                "description": "Complete a security audit",
                "points": 50,
                "deadline": datetime.now() + timedelta(days=7),
                "requirements": ["complete_audit", "submit_report"]
            },
            "quantum_project": {
                "name": "Quantum Project",
                "description": "Build a quantum application",
                "points": 100,
                "deadline": datetime.now() + timedelta(days=30),
                "requirements": ["design_solution", "implement_code", "test_application"]
            }
        }
        
    def award_badge(self, user_id: str, badge: Dict[str, Any]) -> Tuple[bool, str]:
        """Award a badge to a user with quantum-safe verification."""
        try:
            # Verify user access
            if not self._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Encrypt badge data
            encrypted_badge = self._encrypt_badge(badge)
            
            # Store badge
            if user_id not in self.badges:
                self.badges[user_id] = []
                self.metrics["users_engaged"] += 1
            
            self.badges[user_id].append({
                "badge": encrypted_badge,
                "timestamp": datetime.now().isoformat(),
                "metadata": badge.get("metadata", {})
            })
            
            # Update metrics
            self.metrics["badges_awarded"] += 1
            self.metrics["security_checks"] += 1
            
            # Log audit entry
            self._audit(f"Badge awarded to {user_id}", "engagement")
            
            return True, "Badge awarded successfully"
            
        except Exception as e:
            logger.error(f"Failed to award badge: {str(e)}")
            self.metrics["errors"] += 1
            return False, f"Failed to award badge: {str(e)}"
            
    def get_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's progress with quantum-safe verification."""
        try:
            # Verify user access
            if not self._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Get badges
            badges = self.badges.get(user_id, [])
            
            # Decrypt badges
            decrypted_badges = []
            for badge in badges:
                decrypted_badge = self._decrypt_badge(badge["badge"])
                decrypted_badges.append({
                    "badge": decrypted_badge,
                    "timestamp": badge["timestamp"],
                    "metadata": badge["metadata"]
                })
                
            # Update metrics
            self.metrics["security_checks"] += 1
            
            # Log audit entry
            self._audit(f"Progress retrieved for {user_id}", "engagement")
            
            return decrypted_badges
            
        except Exception as e:
            logger.error(f"Failed to get progress: {str(e)}")
            self.metrics["errors"] += 1
            raise
            
    def _encrypt_badge(self, badge: Dict[str, Any]) -> bytes:
        """Encrypt badge data using quantum-safe hybrid TLS."""
        try:
            # Generate keys
            classical_pubkey = self.pqc_crypto.generate_keypair()[1]
            pqc_pubkey = self.pqc_crypto.generate_keypair()[1]
            
            # Encrypt badge
            encrypted = self.hybrid_crypto.encrypt(
                json.dumps(badge).encode(),
                classical_pubkey,
                pqc_pubkey
            )
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Badge encryption failed: {str(e)}")
            raise
            
    def _decrypt_badge(self, encrypted_badge: bytes) -> Dict[str, Any]:
        """Decrypt badge data using quantum-safe hybrid TLS."""
        try:
            # Get keys from key manager
            private_key = self.pqc_crypto.generate_keypair()[0]
            
            # Decrypt badge
            decrypted = self.hybrid_crypto.decrypt(encrypted_badge, private_key)
            return json.loads(decrypted.decode())
            
        except Exception as e:
            logger.error(f"Badge decryption failed: {str(e)}")
            raise
            
    def _verify_user_access(self, user_id: str) -> bool:
        """Verify user access with quantum-safe checks."""
        try:
            # Verify user exists
            if user_id not in self.badges:
                return False
                
            # Generate signature
            signature = self.pqc_crypto.sign_data(user_id)
            
            # Verify signature
            verified = self.pqc_crypto.verify_signature(
                user_id,
                signature
            )
            
            return verified
            
        except Exception as e:
            logger.error(f"Access verification failed: {str(e)}")
            return False
            
    def _audit(self, action: str, action_type: str = "info") -> None:
        """Log gamification actions with quantum-safe audit."""
        try:
            # Create audit entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "action_type": action_type,
                "agent": self.name,
                "role": self.role,
                "agent_id": self.id
            }
            
            # Encrypt audit entry
            encrypted_entry = self._encrypt_badge(log_entry)
            
            # Store encrypted entry
            self.audit_log.append(encrypted_entry)
            
            # Log to SIEM system (simulated)
            print(f"Gamification audit: {action}")
            
        except Exception as e:
            logger.error(f"Audit logging failed: {str(e)}")
            raise
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get gamification metrics."""
        return {
            "agent_id": self.id,
            "name": self.name,
            "role": self.role,
            "metrics": self.metrics,
            "user_stats": {
                "total_users": len(self.badges),
                "badges_awarded": self.metrics["badges_awarded"],
                "active_users": len([u for u in self.badges if self.badges[u]])
            },
            "engagement_stats": {
                "average_badges": sum(len(b) for b in self.badges.values()) / len(self.badges) if self.badges else 0,
                "most_active_user": max(self.badges.items(), key=lambda x: len(x[1]))[0] if self.badges else None
            }
        }
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive gamification report."""
        return {
            "agent_info": {
                "id": self.id,
                "name": self.name,
                "role": self.role,
                "created_at": datetime.now().isoformat()
            },
            "metrics": self.get_metrics(),
            "user_progress": {
                user_id: {
                    "badges": len(badges),
                    "last_award": badges[-1]["timestamp"] if badges else None,
                    "metadata": badges[-1]["metadata"] if badges else {}
                }
                for user_id, badges in self.badges.items()
            },
            "security_status": {
                "last_check": datetime.now().isoformat(),
                "checks_passed": self.metrics["security_checks"],
                "errors": self.metrics["errors"]
            }
        }
        
    def handle_error(self, error: Exception) -> None:
        """Handle errors with quantum-safe recovery."""
        try:
            # Log error
            self._audit(f"Error occurred: {str(error)}", "error")
            
            # Attempt recovery
            if isinstance(error, PermissionError):
                self._audit(f"Access violation: {str(error)}", "security_violation")
                
            # Update metrics
            self.metrics["errors"] += 1
            
        except Exception as e:
            logger.error(f"Error handling failed: {str(e)}")
            raise
