import pytest
import asyncio
from orchestratex.agents.voice_agent import VoiceAgent
from orchestratex.voice.streaming import StreamingVoiceHandler
from orchestratex.agents.quantum_agent import QuantumAgent
from orchestratex.agents.security_agent import SecurityAgent
from orchestratex.agents.gamification_agent import GamificationAgent
from orchestratex.agents.mentor_agent import MentorAgent

@pytest.fixture
def test_config():
    return {
        "voice": {
            "language": "en-US",
            "rate": 16000,
            "chunk": 1024,
            "timeout": 5
        },
        "quantum": {
            "gates": ["Hadamard", "CNOT", "Pauli-Z"],
            "states": ["|0⟩", "|1⟩", "|+⟩", "|-⟩"]
        },
        "security": {
            "key_size": 2048,
            "hash_algo": "sha3_256",
            "encryption": "hybrid"
        },
        "gamification": {
            "badges": ["Quantum Explorer", "Security Master", "Voice Expert"],
            "points": 100
        }
    }

@pytest.fixture
def setup_agents():
    voice_agent = VoiceAgent()
    quantum_agent = QuantumAgent()
    security_agent = SecurityAgent("SecurityAgent", "SecOps")
    gamification_agent = GamificationAgent()
    mentor_agent = MentorAgent("MentorAgent", "Mentorship")
    return {
        "voice": voice_agent,
        "quantum": quantum_agent,
        "security": security_agent,
        "gamification": gamification_agent,
        "mentor": mentor_agent
    }

@pytest.mark.asyncio
async def test_voice_streaming(setup_agents, test_config):
    """Test voice streaming with quantum-safe encryption."""
    voice_agent = setup_agents["voice"]
    streaming_handler = StreamingVoiceHandler(voice_agent)
    
    try:
        # Start stream
        streaming_handler.start_stream()
        
        # Process stream
        await streaming_handler.process_stream()
        
        # Verify metrics
        assert voice_agent.metrics["transcriptions"] > 0
        assert voice_agent.metrics["security_checks"] > 0
        
    finally:
        streaming_handler.stop_stream()

@pytest.mark.asyncio
async def test_quantum_simulation(setup_agents, test_config):
    """Test quantum circuit simulation with security verification."""
    quantum_agent = setup_agents["quantum"]
    security_agent = setup_agents["security"]
    
    # Test circuit simulation
    for gate in test_config["quantum"]["gates"]:
        circuit = f"{gate}"
        result = await quantum_agent.simulate_circuit(circuit)
        assert result is not None
        
    # Verify security
    assert security_agent.verify_quantum_parameters(circuit)

@pytest.mark.asyncio
async def test_gamification_flow(setup_agents, test_config):
    """Test gamification flow with quantum-safe badges."""
    gamification_agent = setup_agents["gamification"]
    user_id = "test_user_001"
    
    # Award badges
    for badge in test_config["gamification"]["badges"]:
        badge_data = {
            "name": badge,
            "description": f"Completed {badge} challenge",
            "points": test_config["gamification"]["points"]
        }
        await gamification_agent.award_badge(user_id, badge_data)
        
    # Verify progress
    progress = await gamification_agent.get_progress(user_id)
    assert len(progress) == len(test_config["gamification"]["badges"])

@pytest.mark.asyncio
async def test_security_scan(setup_agents, test_config):
    """Test security scanning with quantum-safe verification."""
    security_agent = setup_agents["security"]
    
    # Test key generation
    keypair = security_agent.generate_keypair(test_config["security"]["key_size"])
    assert len(keypair[0]) > 0  # Public key
    assert len(keypair[1]) > 0  # Private key
    
    # Test encryption
    message = "Test message"
    encrypted = security_agent.encrypt(message)
    decrypted = security_agent.decrypt(encrypted)
    assert decrypted == message

@pytest.mark.asyncio
async def test_mentor_feedback(setup_agents, test_config):
    """Test mentor feedback with quantum-safe context."""
    mentor_agent = setup_agents["mentor"]
    user_id = "test_user_001"
    
    # Provide feedback
    feedback = await mentor_agent.provide_feedback(
        user_id=user_id,
        activity="quantum_simulation",
        result="success"
    )
    
    # Verify feedback
    assert feedback["rating"] >= 0
    assert feedback["rating"] <= 5
    assert len(feedback["comments"]) > 0

@pytest.mark.asyncio
async def test_performance(setup_agents, test_config):
    """Test performance with multiple concurrent operations."""
    tasks = []
    
    # Create multiple tasks
    for i in range(5):
        tasks.append(asyncio.create_task(
            test_quantum_simulation(setup_agents, test_config)
        ))
        tasks.append(asyncio.create_task(
            test_voice_streaming(setup_agents, test_config)
        ))
    
    # Run tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    pytest.main(["-v", "--cov=orchestratex", "--cov-report=term-missing"])
