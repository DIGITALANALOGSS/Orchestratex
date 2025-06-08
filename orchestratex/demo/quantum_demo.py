from orchestratex.agents.quantum_agent import QuantumAgent
from orchestratex.agents.security_agent import SecurityAgent
from orchestratex.agents.gamification_agent import GamificationAgent
from orchestratex.agents.mentor_agent import MentorAgent
import logging
from typing import Dict, Any
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantumDemo:
    """Demonstrates quantum-safe integration of all agents."""
    
    def __init__(self):
        # Initialize agents
        self.quantum = QuantumAgent()
        self.security = SecurityAgent("SecurityAgent", "SecOps")
        self.gamification = GamificationAgent()
        self.mentor = MentorAgent("MentorAgent", "Mentorship")
        
        # Initialize quantum concepts
        self._initialize_quantum_concepts()
        
    def _initialize_quantum_concepts(self) -> None:
        """Initialize quantum concepts for demonstration."""
        self.concepts = [
            {
                "name": "Superposition",
                "circuit": "Hadamard",
                "state": "|0⟩ + |1⟩",
                "points": 50,
                "badge": "Quantum Explorer"
            },
            {
                "name": "Entanglement",
                "circuit": "Hadamard + CNOT",
                "state": "Bell State",
                "points": 75,
                "badge": "Quantum Master"
            },
            {
                "name": "Interference",
                "circuit": "Hadamard + Pauli-Z + Hadamard",
                "state": "|0⟩ - |1⟩",
                "points": 100,
                "badge": "Quantum Expert"
            }
        ]

    async def run_quantum_concept(self, user_id: str, concept: Dict[str, Any]) -> Dict[str, Any]:
        """Run a quantum concept demonstration."""
        try:
            # Security check
            if not await self.security._verify_user_access(user_id):
                raise PermissionError("Access denied")
                
            # Simulate circuit
            circuit_result = await self.quantum.simulate_circuit(concept["circuit"])
            
            # Visualize state
            visualization = await self.quantum.visualize_state(concept["state"])
            
            # Explain concept
            explanation = await self.quantum.explain_quantum(concept["name"])
            
            # Award badge
            badge = {
                "name": concept["badge"],
                "description": f"Completed {concept['name']} demonstration",
                "points": concept["points"],
                "metadata": {
                    "circuit": concept["circuit"],
                    "state": concept["state"]
                }
            }
            await self.gamification.award_badge(user_id, badge)
            
            # Get mentor feedback
            feedback = await self.mentor.provide_feedback(
                user_id=user_id,
                activity=concept["name"],
                result="success"
            )
            
            return {
                "concept": concept["name"],
                "circuit_result": circuit_result,
                "visualization": visualization,
                "explanation": explanation,
                "badge": badge,
                "feedback": feedback
            }
            
        except Exception as e:
            logger.error(f"Failed to run quantum concept: {str(e)}")
            raise

    async def run_demo(self, user_id: str) -> Dict[str, Any]:
        """Run complete quantum demonstration."""
        try:
            # Initialize results
            results = {
                "user_id": user_id,
                "concepts": [],
                "badges": [],
                "feedback": []
            }
            
            # Run all concepts
            for concept in self.concepts:
                concept_result = await self.run_quantum_concept(user_id, concept)
                results["concepts"].append(concept_result)
                results["badges"].append(concept_result["badge"])
                results["feedback"].append(concept_result["feedback"])
            
            # Get final progress
            progress = await self.gamification.get_progress(user_id)
            results["progress"] = progress
            
            return results
            
        except Exception as e:
            logger.error(f"Demo failed: {str(e)}")
            raise

    def print_results(self, results: Dict[str, Any]) -> None:
        """Print formatted results."""
        print("\n=== Quantum Demonstration Results ===")
        print(f"\nUser ID: {results['user_id']}")
        
        print("\n=== Concepts Demonstrated ===")
        for concept in results["concepts"]:
            print(f"\nConcept: {concept['concept']}")
            print(f"Circuit: {concept['circuit_result']['circuit']}")
            print(f"Badge: {concept['badge']['name']}")
            print(f"Points: {concept['badge']['points']}")
            print(f"Mentor Feedback: {concept['feedback']}")
            
        print("\n=== Badges Earned ===")
        for badge in results["badges"]:
            print(f"- {badge['name']}: {badge['description']}")
            
        print("\n=== Progress ===")
        for item in results["progress"]:
            print(f"- {item['badge']['name']}")

if __name__ == "__main__":
    # Create demo instance
    demo = QuantumDemo()
    
    # Run demo for test user
    user_id = "student_001"
    results = demo.run_demo(user_id)
    
    # Print results
    demo.print_results(results)
