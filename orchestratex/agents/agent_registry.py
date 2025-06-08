import logging
from typing import Dict, List, Optional, Type
from uuid import UUID
from orchestratex.security.quantum.pqc import PQCCryptography, HybridCryptography
from orchestratex.education.quantum_security import QuantumSecurityLesson
from .agent_base import AgentBase, SecurityViolationError

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Registry for managing quantum-safe AI agents with educational integration."""
    
    def __init__(self):
        """Initialize the agent registry with quantum-safe security."""
        self.agents: Dict[str, AgentBase] = {}
        self.agent_types: Dict[str, Type[AgentBase]] = {}
        self.pqc_crypto = PQCCryptography()
        self.hybrid_crypto = HybridCryptography(self.pqc_crypto)
        self.security_lesson = QuantumSecurityLesson("registry_001")
        self.metrics = {
            "registrations": 0,
            "lookups": 0,
            "security_checks": 0,
            "errors": 0
        }
        self.audit_log = []
        
    def register(self, agent: AgentBase) -> None:
        """Register an agent with quantum-safe security checks."""
        try:
            # Verify agent's security
            if not self._verify_agent_security(agent):
                raise SecurityViolationError(
                    "Agent security verification failed",
                    violation_type="security_check_failed",
                    details={"agent_id": agent.id}
                )
                
            # Encrypt agent details
            encrypted_details = self._encrypt_agent_details(agent)
            
            # Store agent
            self.agents[agent.role] = agent
            self.agent_types[agent.role] = type(agent)
            
            # Update metrics
            self.metrics["registrations"] += 1
            self.metrics["security_checks"] += 1
            
            # Log audit entry
            self._log_audit("agent_registered", {
                "agent_id": agent.id,
                "role": agent.role,
                "encrypted_details": encrypted_details
            })
            
        except Exception as e:
            logger.error(f"Agent registration failed: {str(e)}")
            self.metrics["errors"] += 1
            raise
            
    def get(self, role: str) -> Optional[AgentBase]:
        """Get an agent with quantum-safe verification."""
        try:
            # Get agent
            agent = self.agents.get(role)
            if not agent:
                return None
                
            # Verify agent's integrity
            if not self._verify_agent_integrity(agent):
                raise SecurityViolationError(
                    "Agent integrity verification failed",
                    violation_type="integrity_check_failed",
                    details={"role": role}
                )
                
            # Update metrics
            self.metrics["lookups"] += 1
            self.metrics["security_checks"] += 1
            
            # Log audit entry
            self._log_audit("agent_retrieved", {
                "role": role,
                "agent_id": agent.id
            })
            
            return agent
            
        except Exception as e:
            logger.error(f"Agent retrieval failed: {str(e)}")
            self.metrics["errors"] += 1
            raise
            
    def get_all(self) -> List[AgentBase]:
        """Get all registered agents with security verification."""
        try:
            # Verify all agents
            verified_agents = []
            for role, agent in self.agents.items():
                if self._verify_agent_integrity(agent):
                    verified_agents.append(agent)
                    
            # Update metrics
            self.metrics["security_checks"] += len(self.agents)
            
            return verified_agents
            
        except Exception as e:
            logger.error(f"Failed to get all agents: {str(e)}")
            self.metrics["errors"] += 1
            raise
            
    def _verify_agent_security(self, agent: AgentBase) -> bool:
        """Verify agent's security features."""
        try:
            # Check quantum-safe encryption
            test_data = b"security_test"
            encrypted = agent._encrypt_data(test_data)
            decrypted = agent._decrypt_data(encrypted)
            
            # Verify signature
            signature = agent.pqc_crypto.sign_data(test_data)
            verified = agent.pqc_crypto.verify_signature(test_data, signature)
            
            return decrypted == test_data and verified
            
        except Exception as e:
            logger.error(f"Agent security verification failed: {str(e)}")
            return False
            
    def _verify_agent_integrity(self, agent: AgentBase) -> bool:
        """Verify agent's integrity."""
        try:
            # Check agent's ID
            if not isinstance(agent.id, str):
                return False
                
            # Verify agent's role
            if not agent.role:
                return False
                
            # Check security features
            if not hasattr(agent, "pqc_crypto") or not hasattr(agent, "hybrid_crypto"):
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Agent integrity verification failed: {str(e)}")
            return False
            
    def _encrypt_agent_details(self, agent: AgentBase) -> bytes:
        """Encrypt agent details using quantum-safe encryption."""
        try:
            # Create agent details
            details = {
                "agent_id": agent.id,
                "role": agent.role,
                "created_at": datetime.now().isoformat()
            }
            
            # Encrypt using hybrid crypto
            encrypted = self.hybrid_crypto.encrypt(
                json.dumps(details).encode(),
                self.pqc_crypto.generate_keypair()[1],  # Classical key
                self.pqc_crypto.generate_keypair()[1]   # PQC key
            )
            
            return encrypted
            
        except Exception as e:
            logger.error(f"Failed to encrypt agent details: {str(e)}")
            raise
            
    def _log_audit(self, event: str, data: Dict[str, Any]) -> None:
        """Log security-relevant events."""
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        self.audit_log.append(audit_entry)
        logger.info(f"Audit log entry: {event}")
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get registry metrics including security and education."""
        return {
            "total_agents": len(self.agents),
            "metrics": self.metrics,
            "security_progress": self.security_lesson.get_metrics(),
            "education_progress": self.security_lesson.get_progress(),
            "agent_types": list(self.agent_types.keys())
        }
        
    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        return self.audit_log
        
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive registry report."""
        return {
            "registry_info": {
                "created_at": datetime.now().isoformat(),
                "total_agents": len(self.agents)
            },
            "metrics": self.get_metrics(),
            "audit_log": self.get_audit_log(),
            "security_status": {
                "last_check": datetime.now().isoformat(),
                "checks_passed": self.metrics["security_checks"],
                "errors": self.metrics["errors"]
            },
            "agent_summary": {
                role: {
                    "count": len([a for a in self.agents.values() if a.role == role]),
                    "example_id": next((a.id for a in self.agents.values() if a.role == role), None)
                }
                for role in self.agent_types.keys()
            }
        }
        
    def handle_error(self, error: Exception) -> None:
        """Handle errors with quantum-safe recovery."""
        try:
            # Log error
            self._log_audit("error_occurred", {
                "error_type": type(error).__name__,
                "error_message": str(error)
            })
            
            # Attempt recovery
            if isinstance(error, SecurityViolationError):
                self._log_audit("security_violation", {
                    "violation_type": error.violation_type,
                    "details": error.details
                })
                
            # Update metrics
            self.metrics["errors"] += 1
            
        except Exception as e:
            logger.error(f"Error handling failed: {str(e)}")
            raise
