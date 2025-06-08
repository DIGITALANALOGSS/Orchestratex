from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict

from .database import get_db, init_db
from .database.models import User, UserProfile, LearningSession, Content, Assessment, QuantumState, Feedback
from .schemas import auth, user, profile, session, content, assessment, quantum, feedback
from orchestratex.services import (
    AuthService,
    UserService,
    ProfileService,
    SessionService,
    ContentService,
    AssessmentService,
    QuantumService,
    FeedbackService,
    QuantumCircuitService,
    QuantumErrorCorrectionService,
    QuantumSimulationService,
    QuantumAlgorithmsService,
    QuantumDashboardService,
    QuantumMLService,
    QuantumCryptoService
)

# Initialize services
auth_service = AuthService()
user_service = UserService()
profile_service = ProfileService()
session_service = SessionService()
content_service = ContentService()
assessment_service = AssessmentService()
quantum_service = QuantumService()
quantum_circuit_service = QuantumCircuitService()
quantum_error_correction_service = QuantumErrorCorrectionService()
quantum_simulation_service = QuantumSimulationService()
quantum_algorithms_service = QuantumAlgorithmsService()
quantum_dashboard_service = QuantumDashboardService()
quantum_ml_service = QuantumMLService()
quantum_crypto_service = QuantumCryptoService()
feedback_service = FeedbackService()

app = FastAPI(title="Orchestratex API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Dependency for getting current user
async def get_current_user(token: str = Depends(auth_service.oauth2_scheme), db: Session = Depends(get_db)):
    user = auth_service.get_current_user(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# User endpoints
@app.post("/users/", response_model=user.User)
def create_user(user: user.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)

@app.get("/users/me", response_model=user.User)
def read_users_me(current_user: user.User = Depends(get_current_user)):
    return current_user

# Profile endpoints
@app.post("/profiles/", response_model=profile.Profile)
def create_profile(profile: profile.ProfileCreate, db: Session = Depends(get_db)):
    return profile_service.create_profile(db=db, profile=profile)

@app.get("/profiles/{profile_id}", response_model=profile.Profile)
def read_profile(profile_id: int, db: Session = Depends(get_db)):
    db_profile = profile_service.get_profile(db, profile_id=profile_id)
    if db_profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

# Learning Session endpoints
@app.post("/sessions/", response_model=session.Session)
def create_session(session: session.SessionCreate, db: Session = Depends(get_db)):
    return session_service.create_session(db=db, session=session)

@app.get("/sessions/{session_id}", response_model=session.Session)
def read_session(session_id: int, db: Session = Depends(get_db)):
    db_session = session_service.get_session(db, session_id=session_id)
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

# Content endpoints
@app.post("/content/", response_model=content.Content)
def create_content(content: content.ContentCreate, db: Session = Depends(get_db)):
    return content_service.create_content(db=db, content=content)

@app.get("/content/{content_id}", response_model=content.Content)
def read_content(content_id: int, db: Session = Depends(get_db)):
    db_content = content_service.get_content(db, content_id=content_id)
    if db_content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return db_content

# Assessment endpoints
@app.post("/assessments/", response_model=assessment.Assessment)
def create_assessment(assessment: assessment.AssessmentCreate, db: Session = Depends(get_db)):
    return assessment_service.create_assessment(db=db, assessment=assessment)

@app.get("/assessments/{assessment_id}", response_model=assessment.Assessment)
def read_assessment(assessment_id: int, db: Session = Depends(get_db)):
    db_assessment = assessment_service.get_assessment(db, assessment_id=assessment_id)
    if db_assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return db_assessment

# Quantum State endpoints
@app.post("/quantum/states/", response_model=quantum.QuantumState)
def create_quantum_state(state: quantum.QuantumStateCreate, db: Session = Depends(get_db)):
    """Create a new quantum state."""
    return quantum_service.create_quantum_state(db=db, state=state)

@app.get("/quantum/states/{state_id}", response_model=quantum.QuantumState)
def read_quantum_state(state_id: int, db: Session = Depends(get_db)):
    """Get quantum state by ID."""
    db_state = quantum_service.get_quantum_state(db, state_id=state_id)
    if db_state is None:
        raise HTTPException(status_code=404, detail="Quantum state not found")
    return db_state

# Quantum Circuit endpoints
@app.post("/quantum/circuits/", response_model=Dict)
def create_quantum_circuit(
    circuit_data: quantum.QuantumCircuitCreate,
    db: Session = Depends(get_db)
):
    """Create and visualize a quantum circuit."""
    return quantum_circuit_service.create_quantum_circuit(circuit_data)

@app.post("/quantum/circuits/optimize/", response_model=Dict)
def optimize_quantum_circuit(
    circuit_data: quantum.QuantumCircuitCreate,
    db: Session = Depends(get_db)
):
    """Optimize a quantum circuit."""
    return quantum_circuit_service.optimize_circuit(circuit_data)

@app.post("/quantum/circuits/simulate/", response_model=Dict)
def simulate_quantum_circuit(
    circuit_data: quantum.QuantumCircuitCreate,
    db: Session = Depends(get_db)
):
    """Simulate a quantum circuit."""
    return quantum_circuit_service.simulate_circuit(circuit_data)

# Quantum Error Correction endpoints
@app.post("/quantum/error_correction/", response_model=Dict)
def analyze_error_rates(
    quantum_state_id: int,
    db: Session = Depends(get_db)
):
    """Analyze error rates for a quantum state."""
    return quantum_error_correction_service.analyze_error_rates(quantum_state_id)

@app.post("/quantum/error_correction/detect/", response_model=Dict)
def detect_errors(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Detect errors in a quantum state."""
    return quantum_error_correction_service.detect_errors(state_vector)

@app.post("/quantum/error_correction/correct/", response_model=List[complex])
def correct_errors(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Apply error correction to a quantum state."""
    return quantum_error_correction_service.correct_errors(state_vector)

# Quantum Simulation endpoints
@app.post("/quantum/simulations/", response_model=Dict)
def simulate_quantum_algorithm(
    simulation_data: quantum.QuantumSimulationCreate,
    db: Session = Depends(get_db)
):
    """Simulate a quantum algorithm."""
    return quantum_simulation_service.simulate_quantum_algorithm(simulation_data)

@app.post("/quantum/simulations/grover/", response_model=Dict)
def simulate_grover(
    db: Session = Depends(get_db)
):
    """Simulate Grover's algorithm."""
    return quantum_simulation_service._create_grover_circuit()

@app.post("/quantum/simulations/shor/", response_model=Dict)
def simulate_shor(
    db: Session = Depends(get_db)
):
    """Simulate Shor's algorithm."""
    return quantum_simulation_service._create_shor_circuit()

@app.post("/quantum/simulations/vqe/", response_model=Dict)
def simulate_vqe(
    db: Session = Depends(get_db)
):
    """Simulate VQE algorithm."""
    return quantum_simulation_service._create_vqe_circuit()

# Quantum Algorithms endpoints
@app.post("/quantum/algorithms/qft/", response_model=Dict)
def simulate_qft(
    num_qubits: int,
    db: Session = Depends(get_db)
):
    """Simulate Quantum Fourier Transform."""
    return quantum_algorithms_service.create_quantum_fourier_transform(num_qubits)

@app.post("/quantum/algorithms/qpe/", response_model=Dict)
def simulate_qpe(
    num_qubits: int,
    db: Session = Depends(get_db)
):
    """Simulate Quantum Phase Estimation."""
    return quantum_algorithms_service.create_quantum_phase_estimation(num_qubits)

@app.post("/quantum/algorithms/quantum_walk/", response_model=Dict)
def simulate_quantum_walk(
    num_steps: int,
    db: Session = Depends(get_db)
):
    """Simulate Quantum Walk."""
    return quantum_algorithms_service.create_quantum_walk(num_steps)

@app.post("/quantum/algorithms/qnn/", response_model=Dict)
def simulate_quantum_neural_network(
    num_qubits: int,
    db: Session = Depends(get_db)
):
    """Simulate Quantum Neural Network."""
    return quantum_algorithms_service.create_quantum_neural_network(num_qubits)

# Quantum Visualization endpoints
@app.post("/quantum/visualize/state_vector/", response_model=Dict)
def visualize_state_vector(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Visualize quantum state vector."""
    return quantum_dashboard_service.generate_state_vector_visualization(state_vector)

@app.post("/quantum/visualize/qsphere/", response_model=Dict)
def visualize_qsphere(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Visualize quantum state in Q-sphere."""
    return quantum_dashboard_service.generate_qsphere_visualization(state_vector)

@app.post("/quantum/visualize/probability_distribution/", response_model=Dict)
def visualize_probability_distribution(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Visualize quantum state probability distribution."""
    return quantum_dashboard_service.generate_probability_distribution(state_vector)

@app.post("/quantum/visualize/entanglement/", response_model=Dict)
def visualize_entanglement(
    state_vector: List[complex],
    db: Session = Depends(get_db)
):
    """Visualize quantum entanglement."""
    return quantum_dashboard_service.generate_entanglement_visualization(state_vector)

# Quantum ML endpoints
@app.post("/quantum/ml/train/", response_model=Dict)
def train_quantum_classifier(
    data: quantum_ml.QuantumMLTrain,
    db: Session = Depends(get_db)
):
    """Train quantum classifier."""
    return quantum_ml_service.train_quantum_classifier(data.data.X, data.data.y)

@app.post("/quantum/ml/predict/", response_model=Dict)
def predict_quantum_classifier(
    data: quantum_ml.QuantumMLPredict,
    db: Session = Depends(get_db)
):
    """Make predictions with quantum classifier."""
    return quantum_ml_service.evaluate_quantum_classifier(data.classifier, data.X_test)

@app.post("/quantum/ml/cluster/", response_model=Dict)
def quantum_clustering(
    data: quantum_ml.QuantumCluster,
    db: Session = Depends(get_db)
):
    """Perform quantum clustering."""
    return quantum_ml_service.perform_quantum_clustering(data.data, data.num_clusters)

# Quantum Crypto endpoints
@app.post("/quantum/crypto/key/", response_model=Dict)
def generate_quantum_key(
    length: int,
    db: Session = Depends(get_db)
):
    """Generate quantum key."""
    return quantum_crypto_service.generate_quantum_key(length)

@app.post("/quantum/crypto/encrypt/", response_model=Dict)
def quantum_encrypt(
    message: str,
    key: str,
    db: Session = Depends(get_db)
):
    """Encrypt message with quantum key."""
    return quantum_crypto_service.quantum_encryption(message, key)

@app.post("/quantum/crypto/decrypt/", response_model=Dict)
def quantum_decrypt(
    encrypted_message: str,
    key: str,
    db: Session = Depends(get_db)
):
    """Decrypt message with quantum key."""
    return quantum_crypto_service.quantum_decryption(encrypted_message, key)

@app.post("/quantum/crypto/sign/", response_model=Dict)
def quantum_sign(
    message: str,
    db: Session = Depends(get_db)
):
    """Create quantum signature."""
    return quantum_crypto_service.quantum_signature(message)

@app.post("/quantum/crypto/verify/", response_model=Dict)
def quantum_verify(
    message: str,
    signature: str,
    db: Session = Depends(get_db)
):
    """Verify quantum signature."""
    return quantum_crypto_service.verify_quantum_signature(message, signature)

@app.get("/quantum/states/user/{user_id}", response_model=List[quantum.QuantumState])
def get_user_quantum_states(user_id: int, db: Session = Depends(get_db)):
    """Get all quantum states for a user."""
    return quantum_service.get_quantum_states_by_user(user_id)

@app.post("/quantum/states/heal/{state_id}", response_model=quantum.QuantumState)
def heal_quantum_state(state_id: int, db: Session = Depends(get_db)):
    """Apply quantum healing to a state."""
    return quantum_service.apply_quantum_healing(state_id)

@app.post("/quantum/states/teleport/")
def teleport_quantum_state(
    source_id: int,
    target_id: int,
    db: Session = Depends(get_db)
):
    """Teleport quantum state from one user to another."""
    success = quantum_service.teleport_quantum_state(source_id, target_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source or target state not found")
    return {"success": True}

@app.post("/quantum/states/entangle/")
def entangle_quantum_states(
    state1_id: int,
    state2_id: int,
    db: Session = Depends(get_db)
):
    """Entangle two quantum states."""
    state1 = quantum_service.get_quantum_state(state1_id)
    state2 = quantum_service.get_quantum_state(state2_id)
    
    if not state1 or not state2:
        raise HTTPException(status_code=404, detail="One or both states not found")
    
    # Create entangled state
    entangled = quantum_service.create_quantum_state(QuantumStateCreate(
        user_id=state1.user_id,
        state_vector=f"[{state1.state_vector}, {state2.state_vector}]"
    ))
    
    return entangled

@app.post("/quantum/states/measure/")
def measure_quantum_state(
    state_id: int,
    db: Session = Depends(get_db)
):
    """Measure a quantum state."""
    state = quantum_service.get_quantum_state(state_id)
    if not state:
        raise HTTPException(status_code=404, detail="State not found")
    
    # Simulate measurement
    measurement = quantum_service.quantum_healer.measure_state(state.state_vector)
    
    return {
        "state_id": state_id,
        "measurement": measurement,
        "coherence_time": state.coherence_time
    }

# Feedback endpoints
@app.post("/feedback/", response_model=feedback.Feedback)
def create_feedback(feedback: feedback.FeedbackCreate, db: Session = Depends(get_db)):
    return feedback_service.create_feedback(db=db, feedback=feedback)

@app.get("/feedback/{feedback_id}", response_model=feedback.Feedback)
def read_feedback(feedback_id: int, db: Session = Depends(get_db)):
    db_feedback = feedback_service.get_feedback(db, feedback_id=feedback_id)
    if db_feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return db_feedback
