from orchestratex.education.quantum_security import QuantumSecurityLesson, EducationalWorkflow
from orchestratex.security.quantum.pqc import PQCCryptography, QKDChannel, HybridCryptography, QuantumSafeKeyManager
import time
import logging

logging.basicConfig(level=logging.INFO)

# Initialize workflow
workflow = EducationalWorkflow()

# Start lesson for user
user_id = "student_001"
lesson = workflow.start_lesson(user_id)

def run_simulation():
    """Run all quantum security simulations."""
    try:
        # PQC Simulation
        print("\n=== Post-Quantum Cryptography Simulation ===")
        pqc_result = lesson.simulate_pqc()
        print(f"Public Key: {pqc_result['public_key'][:30]}...")
        print(f"Ciphertext: {pqc_result['ciphertext'][:30]}...")
        print(f"Decrypted: {pqc_result['decrypted']}")
        
        # QKD Simulation
        print("\n=== Quantum Key Distribution Simulation ===")
        qkd_result = lesson.simulate_qkd()
        print(f"Shared Key Length: {len(qkd_result['shared_key'])}")
        print(f"Key Bits: {qkd_result['shared_key']}")
        
        # Hybrid Crypto Simulation
        print("\n=== Hybrid Cryptography Simulation ===")
        hybrid_result = lesson.simulate_hybrid()
        print(f"Encrypted Data Length: {len(hybrid_result['encrypted_data'])}")
        
        # Quiz
        print("\n=== Security Quiz ===")
        question = "Why is Post-Quantum Cryptography important?"
        quiz_result = lesson.quiz(question)
        print(f"Quiz Result: {'Correct!' if quiz_result['is_correct'] else 'Incorrect'}")
        print(f"Feedback: {quiz_result['feedback']}")
        
        # Complete lesson
        print("\n=== Lesson Summary ===")
        summary = lesson.complete()
        print(f"Lesson completed for user: {user_id}")
        print(f"Total Attempts: {summary['metrics']['attempts']}")
        print(f"Success Rate: {summary['metrics']['successes']}/{summary['metrics']['attempts']}")
        
        # Generate report
        print("\n=== Progress Report ===")
        report = workflow.generate_report(user_id)
        print(f"Total Events: {report['metrics']['total_events']}")
        print(f"Successful Events: {report['metrics']['successful_events']}")
        print(f"Event Types: {report['metrics']['event_types']}")
        
    except Exception as e:
        logging.error(f"Simulation failed: {str(e)}")
        raise

if __name__ == "__main__":
    print("Starting Quantum Security Demo...")
    run_simulation()
    print("\nDemo completed successfully!")
