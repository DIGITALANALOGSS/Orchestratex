from orchestratex.agents.agent_registry import AgentRegistry
from orchestratex.agents.security_agent import SecurityAgent
from orchestratex.agents.quantum_agent import QuantumAgent
from orchestratex.agents.gamification_agent import GamificationAgent
from orchestratex.agents.mentor_agent import MentorAgent
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantumOrchestrationDemo:
    """Demonstrates quantum-safe orchestration of all agents."""
    
    def __init__(self):
        # Initialize registry and agents
        self.registry = AgentRegistry()
        self._register_agents()
        
    def _register_agents(self) -> None:
        """Register all agents with quantum-safe security."""
        try:
            # Security agent with quantum-safe RBAC
            sec_agent = SecurityAgent(
                name="SecurityAgent",
                role="SecOps",
                quantum_safe=True
            )
            self.registry.register(sec_agent)
            
            # Quantum agent with quantum-safe encryption
            quantum_agent = QuantumAgent(
                name="QuantumAgent",
                role="Quantum",
                quantum_safe=True
            )
            self.registry.register(quantum_agent)
            
            # Gamification agent with quantum-safe badges
            gamification_agent = GamificationAgent()
            self.registry.register(gamification_agent)
            
            # Mentor agent with quantum-safe feedback
            mentor_agent = MentorAgent(
                name="MentorAgent",
                role="Mentorship",
                quantum_safe=True
            )
            self.registry.register(mentor_agent)
            
            logger.info("All agents registered with quantum-safe security")
            
        except Exception as e:
            logger.error(f"Failed to register agents: {str(e)}")
            raise

    async def run_quantum_workflow(self, user_id: str, user_role: str, data: str) -> Dict[str, Any]:
        """Run a quantum-safe orchestration workflow."""
        try:
            # Get agents from registry
            sec = self.registry.get("SecOps")
            quantum = self.registry.get("Quantum")
            game = self.registry.get("Engagement")
            mentor = self.registry.get("Mentorship")
            
            # Security check & quantum-safe encryption
            encrypted = await sec.perform_task({
                "user_role": user_role,
                "data": data
            })
            sec.audit("Data encrypted with quantum-safe encryption")
            
            # Quantum simulation with quantum-safe parameters
            circuit_desc = "Hadamard + CNOT"
            sim_result = await quantum.simulate_circuit(circuit_desc)
            
            # Generate quantum state visualization
            state = "Bell State"
            viz_url = await quantum.visualize_state(state)
            
            # Educational quantum concepts
            quantum_explanation = await quantum.explain_quantum()
            
            # Gamification with quantum-safe badges
            badge = {
                "name": "Quantum Explorer",
                "description": "Completed quantum circuit simulation",
                "points": 50,
                "metadata": {
                    "circuit": circuit_desc,
                    "state": state
                }
            }
            await game.award_badge(user_id, badge)
            
            # Mentorship with quantum-safe feedback
            feedback = await mentor.provide_feedback(
                user_id=user_id,
                activity="quantum_simulation",
                result="success",
                quantum_safe=True
            )
            
            # Generate comprehensive report
            result = {
                "encrypted_data": encrypted,
                "quantum_simulation": sim_result,
                "visualization": viz_url,
                "quantum_concepts": quantum_explanation,
                "badges": await game.get_progress(user_id),
                "mentor_feedback": feedback,
                "security_audit": {
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "user_role": user_role,
                    "status": "success",
                    "quantum_safe": True
                }
            }
            
            logger.info(f"Workflow completed successfully for user {user_id}")
            return result
            
        except PermissionError as e:
            logger.error(f"Access denied: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Workflow failed: {str(e)}")
            raise

    async def run_demo(self) -> None:
        """Run the complete quantum orchestration demo."""
        try:
            # Demo user data
            user_id = "student_001"
            user_role = "admin"
            demo_data = "my secret data"
            
            # Run quantum workflow
            result = await self.run_quantum_workflow(
                user_id=user_id,
                user_role=user_role,
                data=demo_data
            )
            
            # Print results with pretty formatting
            print("\n=== Quantum Orchestration Demo Results ===")
            print(json.dumps(result, indent=2))
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}")
            raise

if __name__ == "__main__":
    # Create and run demo
    demo = QuantumOrchestrationDemo()
    demo.run_demo()
