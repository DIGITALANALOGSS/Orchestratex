import pytest
import asyncio
import numpy as np
from quantum_nexus.quantum_teleportation import QuantumTeleportation

@pytest.mark.asyncio
async def test_standard_teleportation():
    """Test standard quantum teleportation protocol."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("Hello", "standard"),
        ("Quantum", "standard"),
        ("Teleportation", "standard")
    ]
    
    results = await teleporter.test_teleportation(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['success_rate'] >= 0.95, f"Success rate too low for {key}: {result['success_rate']}"

@pytest.mark.asyncio
async def test_entanglement_types():
    """Test different entanglement types."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("Hello", "bell"),
        ("Hello", "ghz"),
        ("Hello", "w")
    ]
    
    results = await teleporter.test_entanglement_types(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['success_rate'] >= 0.95, f"Success rate too low for {key}: {result['success_rate']}"

@pytest.mark.asyncio
async def test_error_correction():
    """Test quantum error correction."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        (np.array([1, 0]), "standard"),
        (np.array([0, 1]), "standard"),
        (np.array([1/np.sqrt(2), 1/np.sqrt(2)]), "standard")
    ]
    
    results = await teleporter.test_error_correction(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['error_rate'] <= 0.05, f"Error rate too high for {key}: {result['error_rate']}"

@pytest.mark.asyncio
async def test_superdense_coding():
    """Test superdense coding protocol."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("00", "superdense"),
        ("01", "superdense"),
        ("10", "superdense"),
        ("11", "superdense")
    ]
    
    results = await teleporter.test_teleportation(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['success_rate'] >= 0.95, f"Success rate too low for {key}: {result['success_rate']}"

@pytest.mark.asyncio
async def test_entanglement_swapping():
    """Test entanglement swapping protocol."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("Hello", "entanglement_swapping"),
        ("Quantum", "entanglement_swapping"),
        ("Teleportation", "entanglement_swapping")
    ]
    
    results = await teleporter.test_teleportation(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['success_rate'] >= 0.95, f"Success rate too low for {key}: {result['success_rate']}"

@pytest.mark.asyncio
async def test_multi_qubit_teleportation():
    """Test multi-qubit teleportation with different protocols."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("Hello", "ghz"),
        ("Hello", "w"),
        ("Hello", "bell")
    ]
    
    results = await teleporter.test_teleportation(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.95, f"Fidelity too low for {key}: {result['fidelity']}"
        assert result['success_rate'] >= 0.95, f"Success rate too low for {key}: {result['success_rate']}"

@pytest.mark.asyncio
async def test_amplitude_encoding():
    """Test amplitude encoding with quantum teleportation."""
    teleporter = QuantumTeleportation()
    
    # Test cases
    test_cases = [
        ("Hello", "standard", "amplitude"),
        ("Quantum", "standard", "amplitude"),
        ("Teleportation", "standard", "amplitude")
    ]
    
    for message, protocol, encoding in test_cases:
        # Prepare message with amplitude encoding
        qc = teleporter.prepare_message(message, encoding)
        state = teleporter.simulator.run(qc).result().get_statevector()
        
        # Teleport state
        teleported = await teleporter.quantum_state_teleportation(state, protocol)
        
        # Calculate fidelity
        fidelity = teleporter._calculate_state_fidelity(state, teleported)
        assert fidelity >= 0.95, f"Fidelity too low for {message} with {encoding}: {fidelity}"

@pytest.mark.asyncio
async def test_teleportation_with_noise():
    """Test teleportation with simulated noise."""
    teleporter = QuantumTeleportation()
    
    # Add noise to simulator
    teleporter.simulator.set_options(noise_model=True)
    
    # Test cases
    test_cases = [
        ("Hello", "standard"),
        ("Quantum", "standard"),
        ("Teleportation", "standard")
    ]
    
    results = await teleporter.test_teleportation(test_cases)
    
    for key, result in results.items():
        assert result['fidelity'] >= 0.85, f"Fidelity too low for {key} with noise: {result['fidelity']}"
        assert result['success_rate'] >= 0.85, f"Success rate too low for {key} with noise: {result['success_rate']}"
