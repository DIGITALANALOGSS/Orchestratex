import json
from datetime import datetime
from typing import List, Dict, Any
import logging
from orchestratex.security.quantum.pqc import PQCCryptography, QKDChannel, HybridCryptography, QuantumSafeKeyManager

logger = logging.getLogger(__name__)

class QuantumSecurityLesson:
    """Interactive quantum security education module."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.key_manager = QuantumSafeKeyManager()
        self.pqc_crypto = PQCCryptography()
        self.qkd_channel = QKDChannel()
        self.hybrid_crypto = HybridCryptography(self.pqc_crypto)
        self.lesson_progress = []
        self.metrics = {
            "attempts": 0,
            "successes": 0,
            "failures": 0,
            "time_spent": 0
        }
        
    def start_lesson(self) -> None:
        """Start the quantum security lesson."""
        self.lesson_progress.append({
            "timestamp": datetime.now().isoformat(),
            "event": "started",
            "user_id": self.user_id
        })
        logger.info(f"Lesson started for user {self.user_id}")
        
    def simulate_pqc(self) -> Dict[str, Any]:
        """Simulate PQC encryption."""
        try:
            # Generate key pair
            priv_key, pub_key = self.pqc_crypto.generate_keypair()
            
            # Encrypt test data
            test_data = b"Quantum Secure Message"
            ciphertext, shared_secret = self.pqc_crypto.encrypt(pub_key, test_data)
            
            # Decrypt
            decrypted = self.pqc_crypto.decrypt(ciphertext, priv_key)
            
            self.lesson_progress.append({
                "timestamp": datetime.now().isoformat(),
                "event": "pqc_simulation",
                "success": True,
                "data_length": len(test_data)
            })
            
            return {
                "public_key": pub_key.decode('utf-8'),
                "ciphertext": ciphertext.decode('utf-8'),
                "shared_secret": shared_secret.decode('utf-8'),
                "decrypted": decrypted.decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"PQC simulation failed: {str(e)}")
            self._record_failure("pqc_simulation")
            raise

    def simulate_qkd(self) -> Dict[str, Any]:
        """Simulate QKD protocol."""
        try:
            # Prepare qubits
            num_qubits = 10
            alice_bits = self.qkd_channel.prepare_qubits(num_qubits)
            alice_bases = [os.urandom(1)[0] % 2 for _ in range(num_qubits)]
            
            # Measure qubits
            bob_bases = [os.urandom(1)[0] % 2 for _ in range(num_qubits)]
            bob_bits = self.qkd_channel.measure_qubits(alice_bases)
            
            # Distribute key
            key = self.qkd_channel.distribute_key(alice_bits, alice_bases, bob_bits, bob_bases)
            
            self.lesson_progress.append({
                "timestamp": datetime.now().isoformat(),
                "event": "qkd_simulation",
                "success": True,
                "key_length": len(key)
            })
            
            return {
                "alice_bits": alice_bits,
                "alice_bases": alice_bases,
                "bob_bits": bob_bits,
                "bob_bases": bob_bases,
                "shared_key": key
            }
            
        except Exception as e:
            logger.error(f"QKD simulation failed: {str(e)}")
            self._record_failure("qkd_simulation")
            raise

    def simulate_hybrid(self) -> Dict[str, Any]:
        """Simulate hybrid cryptography."""
        try:
            # Generate keys
            classical_pubkey = b"classical_pubkey"  # Placeholder
            pqc_pubkey = self.pqc_crypto.generate_keypair()[1]
            
            # Encrypt test data
            test_data = b"Hybrid Secure Message"
            encrypted = self.hybrid_crypto.encrypt(test_data, classical_pubkey, pqc_pubkey)
            
            self.lesson_progress.append({
                "timestamp": datetime.now().isoformat(),
                "event": "hybrid_simulation",
                "success": True,
                "data_length": len(test_data)
            })
            
            return {
                "encrypted_data": encrypted.decode('utf-8'),
                "classical_key": classical_pubkey.decode('utf-8'),
                "pqc_key": pqc_pubkey.decode('utf-8')
            }
            
        except Exception as e:
            logger.error(f"Hybrid crypto simulation failed: {str(e)}")
            self._record_failure("hybrid_simulation")
            raise

    def quiz(self, question: str) -> Dict[str, Any]:
        """Run a security quiz."""
        try:
            correct_answers = [
                "quantum computers",
                "post-quantum cryptography",
                "key distribution",
                "qkd",
                "kyber"
            ]
            
            answer = input(question + " ")
            is_correct = any(keyword in answer.lower() for keyword in correct_answers)
            
            self.lesson_progress.append({
                "timestamp": datetime.now().isoformat(),
                "event": "quiz",
                "question": question,
                "answer": answer,
                "correct": is_correct
            })
            
            self.metrics["attempts"] += 1
            if is_correct:
                self.metrics["successes"] += 1
            else:
                self.metrics["failures"] += 1
            
            return {
                "is_correct": is_correct,
                "feedback": "Correct! Quantum computers can break classical crypto, so PQC is needed." if is_correct else "Review the lesson and try again."
            }
            
        except Exception as e:
            logger.error(f"Quiz failed: {str(e)}")
            self._record_failure("quiz")
            raise

    def complete(self) -> Dict[str, Any]:
        """Complete the lesson and generate report."""
        self.lesson_progress.append({
            "timestamp": datetime.now().isoformat(),
            "event": "completed",
            "user_id": self.user_id
        })
        
        # Generate lesson summary
        summary = {
            "user_id": self.user_id,
            "completion_time": datetime.now().isoformat(),
            "metrics": self.metrics,
            "progress": self.lesson_progress
        }
        
        logger.info(f"Lesson completed for user {self.user_id}")
        return summary

    def _record_failure(self, event_type: str) -> None:
        """Record a failure event."""
        self.lesson_progress.append({
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "success": False,
            "error": "simulation_failed"
        })
        self.metrics["failures"] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get lesson metrics."""
        return self.metrics

    def get_progress(self) -> List[Dict[str, Any]]:
        """Get lesson progress."""
        return self.lesson_progress

class EducationalWorkflow:
    """Orchestrates quantum security education workflow."""
    
    def __init__(self):
        self.lessons = {}
        self.progress_tracker = ProgressTracker()
        
    def start_lesson(self, user_id: str) -> QuantumSecurityLesson:
        """Start a new lesson for a user."""
        lesson = QuantumSecurityLesson(user_id)
        self.lessons[user_id] = lesson
        lesson.start_lesson()
        return lesson
        
    def track_progress(self, user_id: str, progress: List[Dict[str, Any]]) -> None:
        """Track lesson progress."""
        self.progress_tracker.update_progress(user_id, progress)
        
    def generate_report(self, user_id: str) -> Dict[str, Any]:
        """Generate lesson completion report."""
        return self.progress_tracker.generate_report(user_id)

class ProgressTracker:
    """Tracks and analyzes educational progress."""
    
    def __init__(self):
        self.progress_data = {}
        
    def update_progress(self, user_id: str, progress: List[Dict[str, Any]]) -> None:
        """Update user's progress."""
        self.progress_data[user_id] = progress
        
    def generate_report(self, user_id: str) -> Dict[str, Any]:
        """Generate progress report."""
        if user_id not in self.progress_data:
            return {"error": "User not found"}
            
        progress = self.progress_data[user_id]
        metrics = self._analyze_metrics(progress)
        
        return {
            "user_id": user_id,
            "completion_time": progress[-1]["timestamp"],
            "metrics": metrics,
            "progress": progress
        }
        
    def _analyze_metrics(self, progress: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze lesson metrics."""
        metrics = {
            "total_events": len(progress),
            "successful_events": len([p for p in progress if p.get("success", False)]),
            "failed_events": len([p for p in progress if not p.get("success", True)]),
            "event_types": {}
        }
        
        # Count event types
        for event in progress:
            event_type = event.get("event", "unknown")
            metrics["event_types"][event_type] = metrics["event_types"].get(event_type, 0) + 1
        
        return metrics
