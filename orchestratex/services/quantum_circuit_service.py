from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from qiskit import QuantumCircuit, transpile
from qiskit.visualization import circuit_drawer
from orchestratex.database.models import QuantumState
from orchestratex.schemas.quantum import QuantumCircuitCreate, QuantumCircuitUpdate

class QuantumCircuitService:
    def __init__(self, db: Session):
        self.db = db

    def create_quantum_circuit(self, circuit_data: QuantumCircuitCreate) -> Dict:
        """Create and visualize a quantum circuit."""
        # Create quantum circuit
        qc = QuantumCircuit(circuit_data.num_qubits, circuit_data.num_qubits)
        
        # Add gates based on operations
        for operation in circuit_data.operations:
            if operation["gate"] == "h":
                qc.h(operation["qubit"])
            elif operation["gate"] == "x":
                qc.x(operation["qubit"])
            elif operation["gate"] == "cx":
                qc.cx(operation["control"], operation["target"])
            elif operation["gate"] == "measure":
                qc.measure(operation["qubit"], operation["bit"])

        # Transpile for visualization
        transpiled_qc = transpile(qc, basis_gates=['u1', 'u2', 'u3', 'cx'])
        
        # Generate circuit visualization
        circuit_text = circuit_drawer(transpiled_qc, output='text')
        circuit_mpl = circuit_drawer(transpiled_qc, output='mpl')
        
        return {
            "circuit_text": str(circuit_text),
            "circuit_mpl": circuit_mpl,
            "num_qubits": circuit_data.num_qubits,
            "operations": circuit_data.operations
        }

    def optimize_circuit(self, circuit_data: QuantumCircuitCreate) -> Dict:
        """Optimize quantum circuit."""
        qc = self._create_circuit_from_data(circuit_data)
        optimized_qc = transpile(qc, optimization_level=3)
        
        return {
            "optimized_text": str(circuit_drawer(optimized_qc, output='text')),
            "gate_count": optimized_qc.count_ops(),
            "depth": optimized_qc.depth()
        }

    def simulate_circuit(self, circuit_data: QuantumCircuitCreate) -> Dict:
        """Simulate quantum circuit."""
        qc = self._create_circuit_from_data(circuit_data)
        
        # Get statevector simulator
        from qiskit import Aer
        simulator = Aer.get_backend('statevector_simulator')
        
        # Execute circuit
        result = simulator.run(qc).result()
        statevector = result.get_statevector(qc)
        
        return {
            "statevector": str(statevector),
            "probabilities": self._calculate_probabilities(statevector)
        }

    def _create_circuit_from_data(self, circuit_data: QuantumCircuitCreate) -> QuantumCircuit:
        """Helper to create circuit from data."""
        qc = QuantumCircuit(circuit_data.num_qubits, circuit_data.num_qubits)
        for operation in circuit_data.operations:
            if operation["gate"] == "h":
                qc.h(operation["qubit"])
            elif operation["gate"] == "x":
                qc.x(operation["qubit"])
            elif operation["gate"] == "cx":
                qc.cx(operation["control"], operation["target"])
        return qc

    def _calculate_probabilities(self, statevector) -> Dict:
        """Calculate probabilities from statevector."""
        probabilities = {}
        for i, amplitude in enumerate(statevector):
            probabilities[f"|{i:0{len(statevector)-1}b}>"] = abs(amplitude)**2
        return probabilities
