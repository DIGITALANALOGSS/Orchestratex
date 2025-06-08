from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from qiskit.visualization import plot_bloch_multivector, plot_state_qsphere
from qiskit import QuantumCircuit
import matplotlib.pyplot as plt
import numpy as np
from orchestratex.database.models import QuantumState

class QuantumDashboardService:
    def __init__(self, db: Session):
        self.db = db

    def generate_state_vector_visualization(self, state_vector: List[complex]) -> Dict:
        """Generate Bloch sphere visualization of state vector."""
        # Create Bloch sphere plot
        plot_bloch_multivector(state_vector)
        plt.savefig('bloch_sphere.png')
        
        return {
            "type": "bloch_sphere",
            "file": "bloch_sphere.png",
            "state_vector": state_vector
        }

    def generate_qsphere_visualization(self, state_vector: List[complex]) -> Dict:
        """Generate Q-sphere visualization."""
        # Create Q-sphere plot
        plot_state_qsphere(state_vector)
        plt.savefig('qsphere.png')
        
        return {
            "type": "qsphere",
            "file": "qsphere.png",
            "state_vector": state_vector
        }

    def generate_probability_distribution(self, state_vector: List[complex]) -> Dict:
        """Generate probability distribution visualization."""
        probabilities = [abs(x)**2 for x in state_vector]
        
        plt.figure(figsize=(10, 5))
        plt.bar(range(len(probabilities)), probabilities)
        plt.xlabel('States')
        plt.ylabel('Probability')
        plt.title('Quantum State Probability Distribution')
        plt.xticks(range(len(probabilities)), [bin(i)[2:].zfill(len(state_vector)) for i in range(len(probabilities))])
        plt.savefig('probability_distribution.png')
        
        return {
            "type": "probability_distribution",
            "file": "probability_distribution.png",
            "probabilities": probabilities
        }

    def generate_entanglement_visualization(self, state_vector: List[complex]) -> Dict:
        """Generate entanglement visualization."""
        # Calculate concurrence for 2-qubit states
        if len(state_vector) == 4:
            rho = np.outer(state_vector, np.conj(state_vector))
            sigma_y = np.array([[0, -1j], [1j, 0]])
            rho_tilde = np.dot(np.dot(np.kron(sigma_y, sigma_y), rho.conj()), np.kron(sigma_y, sigma_y))
            eigenvalues = np.sort(np.abs(np.linalg.eigvals(rho_tilde)))[::-1]
            concurrence = max(0, np.sqrt(eigenvalues[0]) - np.sqrt(eigenvalues[1]) - np.sqrt(eigenvalues[2]) - np.sqrt(eigenvalues[3]))
            
            plt.figure(figsize=(8, 8))
            plt.pie([concurrence, 1-concurrence], labels=["Entangled", "Separable"], autopct='%1.1f%%')
            plt.title('Entanglement Measure')
            plt.savefig('entanglement.png')
            
            return {
                "type": "entanglement",
                "file": "entanglement.png",
                "concurrence": concurrence
            }
        
        return {"error": "Entanglement visualization only supported for 2-qubit states"}

    def generate_all_visualizations(self, state_vector: List[complex]) -> Dict:
        """Generate all available visualizations for a state vector."""
        return {
            "bloch_sphere": self.generate_state_vector_visualization(state_vector),
            "qsphere": self.generate_qsphere_visualization(state_vector),
            "probability_distribution": self.generate_probability_distribution(state_vector),
            "entanglement": self.generate_entanglement_visualization(state_vector) if len(state_vector) == 4 else None
        }
