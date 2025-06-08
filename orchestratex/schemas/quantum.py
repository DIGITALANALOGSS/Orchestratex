from typing import List, Dict, Optional
from pydantic import BaseModel

class QuantumCircuitCreate(BaseModel):
    num_qubits: int
    operations: List[Dict]
    custom_operations: Optional[List[Dict]] = None

class QuantumCircuitUpdate(BaseModel):
    operations: List[Dict]
    custom_operations: Optional[List[Dict]] = None

class QuantumErrorCorrectionCreate(BaseModel):
    state_vector: List[complex]
    error_type: str
    correction_method: str

class QuantumSimulationCreate(BaseModel):
    algorithm_type: str
    num_qubits: int
    custom_operations: Optional[List[Dict]] = None
    backend: str = "simulator"

class QuantumState(BaseModel):
    id: int
    user_id: int
    state_vector: List[complex]
    coherence_time: float
    error_rate: float
    created_at: str
    updated_at: str

class QuantumStateCreate(BaseModel):
    user_id: int
    state_vector: List[complex]

class QuantumStateUpdate(BaseModel):
    state_vector: List[complex]
    coherence_time: Optional[float] = None
    error_rate: Optional[float] = None
