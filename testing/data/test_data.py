import json
import os
from datetime import datetime
import random
import string

class TestDataGenerator:
    def __init__(self, output_dir: str = "test_data"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_quantum_test_data(self, num_samples: int = 100) -> None:
        """Generate test data for quantum operations."""
        test_data = []
        
        for _ in range(num_samples):
            test_case = {
                "circuit": self._generate_quantum_circuit(),
                "expected_output": self._generate_expected_output(),
                "parameters": self._generate_parameters(),
                "timestamp": datetime.now().isoformat()
            }
            test_data.append(test_case)
            
        self._save_test_data(test_data, "quantum_test_data.json")

    def generate_performance_test_data(self, num_samples: int = 1000) -> None:
        """Generate test data for performance testing."""
        test_data = []
        
        for _ in range(num_samples):
            test_case = {
                "operation": random.choice(["encryption", "decryption", "key_exchange"]),
                "data_size": random.randint(1024, 1048576),  # 1KB to 1MB
                "expected_time": random.uniform(0.1, 10.0),  # 0.1s to 10s
                "timestamp": datetime.now().isoformat()
            }
            test_data.append(test_case)
            
        self._save_test_data(test_data, "performance_test_data.json")

    def generate_security_test_data(self, num_samples: int = 50) -> None:
        """Generate test data for security testing."""
        test_data = []
        
        for _ in range(num_samples):
            test_case = {
                "attack_type": random.choice([
                    "quantum_attack",
                    "side_channel",
                    "man_in_middle",
                    "brute_force"
                ]),
                "target": random.choice([
                    "encryption",
                    "authentication",
                    "authorization",
                    "data_integrity"
                ]),
                "expected_result": random.choice(["pass", "fail"]),
                "timestamp": datetime.now().isoformat()
            }
            test_data.append(test_case)
            
        self._save_test_data(test_data, "security_test_data.json")

    def _generate_quantum_circuit(self) -> dict:
        """Generate a random quantum circuit."""
        return {
            "qubits": random.randint(2, 10),
            "gates": random.randint(10, 100),
            "depth": random.randint(10, 50),
            "operations": random.choices([
                "h", "x", "y", "z", "cx", "cz", "swap",
                "t", "s", "tdg", "sdg"
            ], k=random.randint(10, 50))
        }

    def _generate_expected_output(self) -> dict:
        """Generate expected output for a quantum circuit."""
        return {
            "state_vector": self._random_complex_vector(),
            "measurement": self._random_measurement(),
            "error_rate": random.uniform(0.0, 0.1)
        }

    def _generate_parameters(self) -> dict:
        """Generate parameters for quantum operations."""
        return {
            "shots": random.randint(1000, 10000),
            "backend": random.choice([
                "aer_simulator",
                "ibmq_qasm_simulator",
                "ibmq_armonk"
            ]),
            "optimization_level": random.randint(0, 3)
        }

    def _random_complex_vector(self, size: int = 16) -> list:
        """Generate a random complex vector."""
        return [
            complex(random.uniform(-1, 1), random.uniform(-1, 1))
            for _ in range(size)
        ]

    def _random_measurement(self, size: int = 16) -> dict:
        """Generate random measurement results."""
        results = {}
        for i in range(size):
            state = format(i, 'b').zfill(4)
            results[state] = random.randint(0, 1000)
        return results

    def _save_test_data(self, data: list, filename: str) -> None:
        """Save test data to JSON file."""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    generator = TestDataGenerator()
    generator.generate_quantum_test_data()
    generator.generate_performance_test_data()
    generator.generate_security_test_data()
