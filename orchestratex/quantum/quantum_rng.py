from qiskit import QuantumCircuit, execute, Aer
import numpy as np

class QuantumRNG:
    """Quantum Random Number Generator."""
    
    def __init__(self):
        self.simulator = Aer.get_backend('qasm_simulator')
        
    def generate(self, n_bits: int = 32) -> int:
        """
        Generate quantum random number.
        
        Args:
            n_bits: Number of bits for the random number
            
        Returns:
            Quantum random number
        """
        circuit = QuantumCircuit(n_bits)
        
        # Apply Hadamard gates for superposition
        for qubit in range(n_bits):
            circuit.h(qubit)
        
        # Measure all qubits
        circuit.measure_all()
        
        # Execute circuit
        result = execute(circuit, self.simulator, shots=1).result()
        counts = result.get_counts()
        
        # Get binary result and convert to integer
        binary_result = list(counts.keys())[0]
        return int(binary_result, 2)
        
    def generate_float(self) -> float:
        """Generate quantum random float between 0 and 1."""
        return self.generate(32) / (2**32 - 1)
        
    def generate_normal(self, mean: float = 0, std: float = 1) -> float:
        """
        Generate quantum random number from normal distribution.
        
        Args:
            mean: Mean of the distribution
            std: Standard deviation of the distribution
            
        Returns:
            Quantum random number from normal distribution
        """
        # Generate two uniform random numbers
        u1 = self.generate_float()
        u2 = self.generate_float()
        
        # Box-Muller transform
        z0 = np.sqrt(-2 * np.log(u1)) * np.cos(2 * np.pi * u2)
        return mean + std * z0
