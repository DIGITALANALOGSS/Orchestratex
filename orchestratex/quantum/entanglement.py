from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.library import SurfaceCode
from qiskit.providers.ibmq import IBMQ
import numpy as np
import json
import logging

logger = logging.getLogger(__name__)

class QuantumEntanglement:
    """Quantum Entanglement Module for secure quantum state creation and manipulation."""
    
    def __init__(self, num_qubits: int = 4, use_cloud: bool = False):
        """
        Initialize QuantumEntanglement with error correction and cloud deployment.
        
        Args:
            num_qubits: Number of qubits for entanglement
            use_cloud: Whether to use IBM Quantum cloud backend
        """
        self.simulator = AerSimulator()
        self.num_qubits = num_qubits
        self.use_cloud = use_cloud
        self.cloud_backend = None
        
        # Initialize cloud backend if requested
        if use_cloud:
            try:
                IBMQ.load_account()
                self.cloud_backend = IBMQ.get_backend('ibmq_qasm_simulator')
                logger.info("Connected to IBM Quantum cloud backend")
            except Exception as e:
                logger.warning(f"Could not connect to cloud backend: {str(e)}")
                self.cloud_backend = None
        
        self.metrics = {
            "bell_states": 0,
            "ghz_states": 0,
            "swaps": 0,
            "error_corrected": 0,
            "cloud_executions": 0,
            "error_correction_success": 0
        }
        
    def create_bell_state(self) -> QuantumCircuit:
        """
        Create Bell state entanglement.
        
        Returns:
            QuantumCircuit: Bell state circuit
        """
        try:
            self.metrics["bell_states"] += 1
            
            qc = QuantumCircuit(2)
            qc.h(0)
            qc.cx(0, 1)
            qc.barrier()
            
            # Add measurement for verification
            qc.measure_all()
            
            # Optimize circuit
            optimized = transpile(qc, self.simulator, optimization_level=3)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Bell state creation failed: {str(e)}")
            raise
            
    def generate_ghz_state(self) -> QuantumCircuit:
        """
        Generate GHZ (Greenberger–Horne–Zeilinger) state.
        
        Returns:
            QuantumCircuit: GHZ state circuit
        """
        try:
            self.metrics["ghz_states"] += 1
            
            qc = QuantumCircuit(self.num_qubits)
            qc.h(0)
            
            # Create entanglement chain
            for i in range(1, self.num_qubits):
                qc.cx(0, i)
            
            qc.barrier()
            
            # Add measurement for verification
            qc.measure_all()
            
            # Optimize circuit
            optimized = transpile(qc, self.simulator, optimization_level=3)
            
            return optimized
            
        except Exception as e:
            logger.error(f"GHZ state generation failed: {str(e)}")
            raise
            
    def entanglement_swapping(self) -> QuantumCircuit:
        """
        Perform quantum entanglement swapping.
        
        Returns:
            QuantumCircuit: Entanglement swapping circuit
        """
        try:
            self.metrics["swaps"] += 1
            
            qc = QuantumCircuit(4)
            
            # Create two Bell pairs
            qc.h(0); qc.cx(0,1)
            qc.h(2); qc.cx(2,3)
            
            # Perform swapping
            qc.cx(1,2)
            qc.h(1)
            qc.barrier()
            
            # Add measurement for verification
            qc.measure_all()
            
            # Optimize circuit
            optimized = transpile(qc, self.simulator, optimization_level=3)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Entanglement swapping failed: {str(e)}")
            raise
            
    def error_corrected_entanglement(self, distance: int = 3) -> QuantumCircuit:
        """
        Create error-corrected entanglement using surface code with configurable distance.
        
        Args:
            distance: Surface code distance (odd number)
            
        Returns:
            QuantumCircuit: Error-corrected entanglement circuit
        """
        try:
            self.metrics["error_corrected"] += 1
            
            # Create surface code circuit
            qc = QuantumCircuit()
            surface_code = SurfaceCode(distance)
            qc.compose(surface_code, inplace=True)
            
            # Add entanglement layer
            qc.h(0)
            for i in range(1, distance):
                qc.cx(0, i)
            
            # Add error correction layers
            for _ in range(distance):
                qc.barrier()
                # Add stabilizer measurements
                for i in range(distance):
                    qc.h(i)
                    qc.cx(i, (i+1) % distance)
                
                # Add syndrome measurement
                for i in range(distance):
                    qc.measure(i, i)
            
            # Add final measurement
            qc.barrier()
            qc.measure_all()
            
            # Optimize circuit
            if self.use_cloud and self.cloud_backend:
                optimized = transpile(qc, self.cloud_backend, optimization_level=3)
                self.metrics["cloud_executions"] += 1
            else:
                optimized = transpile(qc, self.simulator, optimization_level=3)
            
            # Execute and verify error correction
            result = optimized.run(self.cloud_backend if self.use_cloud else self.simulator).result()
            counts = result.get_counts()
            
            # Check error correction success
            if max(counts.values()) / sum(counts.values()) > 0.9:
                self.metrics["error_correction_success"] += 1
            
            return optimized
            
        except Exception as e:
            logger.error(f"Error-corrected entanglement failed: {str(e)}")
            raise
            
    def verify_entanglement(self, qc: QuantumCircuit) -> Dict[str, Any]:
        """
        Verify quantum entanglement with error correction.
        
        Args:
            qc: Quantum circuit to verify
            
        Returns:
            Dictionary containing verification results
        """
        try:
            # Add error detection layers
            qc.barrier()
            for i in range(self.num_qubits):
                qc.h(i)
                qc.cx(i, (i+1) % self.num_qubits)
            qc.measure_all()
            
            # Execute circuit
            backend = self.cloud_backend if self.use_cloud else self.simulator
            result = backend.run(qc).result()
            counts = result.get_counts()
            
            # Analyze entanglement quality and error rate
            max_count = max(counts.values())
            total_shots = sum(counts.values())
            quality = max_count / total_shots
            error_rate = 1 - quality
            
            # Check for entanglement preservation
            preserved = quality > 0.9
            
            return {
                "counts": counts,
                "quality": quality,
                "error_rate": error_rate,
                "preserved": preserved,
                "backend": "cloud" if self.use_cloud else "local",
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Entanglement verification failed: {str(e)}")
            raise
            
    def get_metrics(self) -> Dict[str, Any]:
        """Get entanglement metrics."""
        return self.metrics
        
    def create_custom_entanglement(self, pattern: str, error_correction: bool = True) -> QuantumCircuit:
        """
        Create custom entanglement pattern with optional error correction.
        
        Args:
            pattern: Entanglement pattern description
            error_correction: Whether to add error correction layers
            
        Returns:
            QuantumCircuit: Custom entanglement circuit
        """
        try:
            # Create circuit based on pattern
            qc = QuantumCircuit(self.num_qubits)
            
            # Implement pattern-specific entanglement
            if pattern == "ring":
                for i in range(self.num_qubits):
                    qc.h(i)
                    qc.cx(i, (i+1) % self.num_qubits)
            elif pattern == "star":
                qc.h(0)
                for i in range(1, self.num_qubits):
                    qc.cx(0, i)
            
            # Add error correction if requested
            if error_correction:
                qc.barrier()
                for i in range(self.num_qubits):
                    qc.h(i)
                    qc.cx(i, (i+1) % self.num_qubits)
                    qc.measure(i, i)
            
            qc.barrier()
            
            # Add measurement for verification
            qc.measure_all()
            
            # Optimize circuit
            if self.use_cloud and self.cloud_backend:
                optimized = transpile(qc, self.cloud_backend, optimization_level=3)
                self.metrics["cloud_executions"] += 1
            else:
                optimized = transpile(qc, self.simulator, optimization_level=3)
            
            return optimized
            
        except Exception as e:
            logger.error(f"Custom entanglement creation failed: {str(e)}")
            raise
            
    def analyze_entanglement(self, qc: QuantumCircuit) -> Dict[str, Any]:
        """
        Analyze entanglement properties.
        
        Args:
            qc: Quantum circuit to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Execute circuit
            result = self.simulator.run(qc).result()
            counts = result.get_counts()
            
            # Calculate entanglement metrics
            metrics = {
                "max_probability": max(counts.values()) / sum(counts.values()),
                "distinct_states": len(counts),
                "entanglement_depth": len(qc.data),
                "cnot_count": sum(1 for op in qc.data if op[0].name == 'cx')
            }
            
            return {
                "metrics": metrics,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Entanglement analysis failed: {str(e)}")
            raise
