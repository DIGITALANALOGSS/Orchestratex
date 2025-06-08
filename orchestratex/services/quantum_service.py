from typing import List, Optional
from sqlalchemy.orm import Session
from orchestratex.database.models import QuantumState
from orchestratex.schemas.quantum import QuantumStateCreate, QuantumStateUpdate
from quantum_nexus.quantum_healing import QuantumHealingCore
from quantum_nexus.quantum_teleportation import QuantumTeleportation
from quantum_nexus.qa_solver import QuantumAnnealer

class QuantumService:
    def __init__(self, db: Session):
        self.db = db
        self.quantum_healer = QuantumHealingCore()
        self.quantum_teleporter = QuantumTeleportation()
        self.qa_solver = QuantumAnnealer()

    def get_quantum_state(self, state_id: int) -> Optional[QuantumState]:
        """Get quantum state by ID."""
        return self.db.query(QuantumState).filter(QuantumState.id == state_id).first()

    def get_quantum_states(self, skip: int = 0, limit: int = 100) -> List[QuantumState]:
        """Get list of quantum states."""
        return self.db.query(QuantumState).offset(skip).limit(limit).all()

    def get_quantum_states_by_user(self, user_id: int) -> List[QuantumState]:
        """Get quantum states by user ID."""
        return self.db.query(QuantumState).filter(QuantumState.user_id == user_id).all()

    def create_quantum_state(self, state: QuantumStateCreate) -> QuantumState:
        """Create new quantum state."""
        # Prepare quantum state
        state_vector = self.quantum_teleporter.prepare_message(state.state_vector)
        
        # Apply quantum healing
        healed = self.quantum_healer.heal_state(state_vector)
        
        # Calculate coherence time and error rate
        coherence_time = self.quantum_healer.get_coherence_time(healed)
        error_rate = self.quantum_healer.get_error_rate(healed)
        
        db_state = QuantumState(
            user_id=state.user_id,
            state_vector=healed,
            coherence_time=coherence_time,
            error_rate=error_rate
        )
        self.db.add(db_state)
        self.db.commit()
        self.db.refresh(db_state)
        return db_state

    def update_quantum_state(self, state_id: int, state: QuantumStateUpdate) -> Optional[QuantumState]:
        """Update quantum state."""
        db_state = self.get_quantum_state(state_id)
        if db_state:
            for key, value in state.model_dump(exclude_unset=True).items():
                setattr(db_state, key, value)
            self.db.commit()
            self.db.refresh(db_state)
        return db_state

    def apply_quantum_healing(self, state_id: int) -> Optional[QuantumState]:
        """Apply quantum healing to a state."""
        db_state = self.get_quantum_state(state_id)
        if db_state:
            healed = self.quantum_healer.heal_state(db_state.state_vector)
            db_state.state_vector = healed
            db_state.coherence_time = self.quantum_healer.get_coherence_time(healed)
            db_state.error_rate = self.quantum_healer.get_error_rate(healed)
            self.db.commit()
            self.db.refresh(db_state)
        return db_state

    def teleport_quantum_state(self, source_id: int, target_id: int) -> bool:
        """Teleport quantum state from one user to another."""
        source_state = self.get_quantum_state(source_id)
        target_state = self.get_quantum_state(target_id)
        
        if source_state and target_state:
            teleported = self.quantum_teleporter.teleport_state(
                source_state.state_vector,
                target_state.state_vector
            )
            target_state.state_vector = teleported
            self.db.commit()
            return True
        return False

    def delete_quantum_state(self, state_id: int) -> bool:
        """Delete quantum state."""
        db_state = self.get_quantum_state(state_id)
        if db_state:
            self.db.delete(db_state)
            self.db.commit()
            return True
        return False
