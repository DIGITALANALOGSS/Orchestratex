import logging
import numpy as np
from qiskit import QuantumCircuit, Aer, execute
from qiskit.circuit.library import QFT, GroverOperator
from qiskit.algorithms import Shor
from qiskit.utils import QuantumInstance
from typing import List, Tuple, Dict, Any
import math

class QuantumAlgorithms:
    def __init__(self, backend: str = 'aer_simulator'):
        """Initialize quantum algorithms.
        
        Args:
            backend: Quantum backend to use
        """
        self.backend = backend
        self.logger = logging.getLogger(__name__)
        self.quantum_instance = QuantumInstance(Aer.get_backend(backend))
        
    def grover_search(self, n: int, oracle: List[int]) -> Tuple[int, Dict[str, Any]]:
        """Implement Grover's search algorithm.
        
        Args:
            n: Number of qubits
            oracle: List of marked items
            
        Returns:
            Tuple containing result and metrics
        """
        try:
            # Create quantum circuit
            qc = QuantumCircuit(n)
            
            # Apply Hadamard gates
            for qubit in range(n):
                qc.h(qubit)
            
            # Create oracle
            for item in oracle:
                binary = format(item, f'0{n}b')
                for i, bit in enumerate(binary):
                    if bit == '0':
                        qc.x(i)
                
            # Apply Grover operator
            grover = GroverOperator(oracle)
            qc.append(grover, range(n))
            
            # Measure
            qc.measure_all()
            
            # Execute
            result = execute(qc, Aer.get_backend('aer_simulator')).result()
            counts = result.get_counts(qc)
            
            # Find most probable result
            max_count = max(counts.values())
            best_result = [k for k, v in counts.items() if v == max_count][0]
            
            return int(best_result, 2), {
                'iterations': grover.num_iterations,
                'probability': max_count / sum(counts.values()),
                'circuit_depth': qc.depth(),
                'num_qubits': n
            }
            
        except Exception as e:
            self.logger.error(f"Grover search failed: {str(e)}")
            raise
            
    def shor_factorization(self, N: int) -> Tuple[int, int, Dict[str, Any]]:
        """Implement Shor's factorization algorithm.
        
        Args:
            N: Number to factorize
            
        Returns:
            Tuple containing factors and metrics
        """
        try:
            # Initialize Shor's algorithm
            shor = Shor()
            
            # Run algorithm
            result = shor.factor(N, quantum_instance=self.quantum_instance)
            
            # Extract factors
            factors = result.factors
            
            return factors[0], factors[1], {
                'num_qubits': result.num_qubits,
                'circuit_depth': result.circuit_depth,
                'probability': result.probability,
                'runtime': result.runtime
            }
            
        except Exception as e:
            self.logger.error(f"Shor factorization failed: {str(e)}")
            raise
            
    def quantum_fourier_transform(self, n: int) -> QuantumCircuit:
        """Implement Quantum Fourier Transform.
        
        Args:
            n: Number of qubits
            
        Returns:
            Quantum circuit implementing QFT
        """
        try:
            qc = QuantumCircuit(n)
            
            # Apply QFT
            for i in range(n):
                qc.h(i)
                for j in range(i+1, n):
                    qc.cp(math.pi/2**(j-i), j, i)
            
            # Swap qubits
            for i in range(n//2):
                qc.swap(i, n-i-1)
            
            return qc
            
        except Exception as e:
            self.logger.error(f"QFT failed: {str(e)}")
            raise
            
    def quantum_phase_estimation(self, unitary: QuantumCircuit, n: int) -> Tuple[float, Dict[str, Any]]:
        """Implement Quantum Phase Estimation.
        
        Args:
            unitary: Unitary operator
            n: Number of qubits
            
        Returns:
            Tuple containing phase and metrics
        """
        try:
            # Create circuit
            qc = QuantumCircuit(n)
            
            # Apply Hadamard gates
            for i in range(n):
                qc.h(i)
            
            # Apply controlled-U operations
            for i in range(n):
                qc.append(unitary, [i])
            
            # Apply inverse QFT
            qc.append(QFT(n, inverse=True), range(n))
            
            # Measure
            qc.measure_all()
            
            # Execute
            result = execute(qc, Aer.get_backend('aer_simulator')).result()
            counts = result.get_counts(qc)
            
            # Calculate phase
            max_count = max(counts.values())
            best_result = [k for k, v in counts.items() if v == max_count][0]
            phase = int(best_result, 2) / 2**n
            
            return phase, {
                'circuit_depth': qc.depth(),
                'num_qubits': n,
                'probability': max_count / sum(counts.values())
            }
            
        except Exception as e:
            self.logger.error(f"Phase estimation failed: {str(e)}")
            raise
            
    def variational_quantum_eigensolver(self, hamiltonian: List[List[float]], n: int) -> Tuple[float, Dict[str, Any]]:
        """Implement Variational Quantum Eigensolver.
        
        Args:
            hamiltonian: Hamiltonian matrix
            n: Number of qubits
            
        Returns:
            Tuple containing eigenvalue and metrics
        """
        try:
            # Create circuit
            qc = QuantumCircuit(n)
            
            # Initialize parameters
            params = np.random.random(n)
            
            # Apply variational ansatz
            for i in range(n):
                qc.rx(params[i], i)
            
            # Measure
            qc.measure_all()
            
            # Execute
            result = execute(qc, Aer.get_backend('aer_simulator')).result()
            counts = result.get_counts(qc)
            
            # Calculate expectation value
            expectation = 0
            for state, count in counts.items():
                # Convert state to binary
                binary = [int(bit) for bit in state]
                # Calculate energy
                energy = np.dot(binary, np.dot(hamiltonian, binary))
                expectation += energy * (count / sum(counts.values()))
            
            return expectation, {
                'circuit_depth': qc.depth(),
                'num_qubits': n,
                'num_parameters': len(params),
                'runtime': result.time_taken
            }
            
        except Exception as e:
            self.logger.error(f"VQE failed: {str(e)}")
            raise
