import pytest
from orchestratex.agents import voice_agent
from orchestratex.models import rag_maestro
import numpy as np
import random
import string

@pytest.fixture
def mock_voice_agent():
    return voice_agent.VoiceAgent(get_settings())

@pytest.fixture
def mock_rag_maestro():
    return rag_maestro(get_settings())

# Test various types of noise injection
@pytest.mark.parametrize("noise_type", [
    "typographical",
    "background",
    "network",
    "api_failure"
])
def test_noise_injection(noise_type, mock_voice_agent, monkeypatch):
    input_text = "What is the weather today?"
    
    if noise_type == "typographical":
        noisy_input = add_typographical_noise(input_text)
    elif noise_type == "background":
        noisy_input = add_background_noise(input_text)
    elif noise_type == "network":
        noisy_input = input_text
        monkeypatch.setattr(mock_voice_agent, "transcribe", simulate_network_delay)
    elif noise_type == "api_failure":
        noisy_input = input_text
        monkeypatch.setattr(mock_voice_agent, "transcribe", simulate_api_failure)
    
    try:
        result = mock_voice_agent.transcribe(noisy_input)
        assert result is not None
        assert len(result) > 0
    except Exception as e:
        assert isinstance(e, voice_agent.VoiceAgentError)
        assert "noise" in str(e).lower() or "failure" in str(e).lower()

def test_api_failure_simulation(monkeypatch):
    def fail_api(*args, **kwargs):
        raise Exception("Simulated API failure")
    
    monkeypatch.setattr(voice_agent.VoiceAgent, "transcribe", fail_api)
    
    agent = voice_agent.VoiceAgent(get_settings())
    with pytest.raises(Exception):
        agent.transcribe("test")

def test_input_distribution_shift():
    # Test with extremely long input
    long_input = "a" * 100000
    agent = voice_agent.VoiceAgent(get_settings())
    
    with pytest.raises(voice_agent.VoiceAgentError):
        agent.transcribe(long_input)
    
    # Test with non-text input
    non_text_input = b"\x00\x01\x02"
    with pytest.raises(voice_agent.VoiceAgentError):
        agent.transcribe(non_text_input)

def test_concurrent_noise_injection():
    import concurrent.futures
    
    agent = voice_agent.VoiceAgent(get_settings())
    inputs = [
        add_typographical_noise("Hello"),
        add_background_noise("How are you?"),
        "What's up?"  # Clean input
    ]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(agent.transcribe, input) for input in inputs]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                assert result is not None
            except Exception as e:
                assert isinstance(e, voice_agent.VoiceAgentError)

def test_resource_exhaustion():
    agent = voice_agent.VoiceAgent(get_settings())
    
    # Simulate many concurrent requests
    for _ in range(100):
        try:
            agent.transcribe("test")
        except Exception as e:
            assert isinstance(e, voice_agent.VoiceAgentError)
            assert "resource" in str(e).lower()

def add_typographical_noise(text: str) -> str:
    """Add typographical errors to text."""
    noisy_text = ""
    for char in text:
        if random.random() < 0.1:  # 10% chance of error
            # Randomly choose between:
            # 1. Replace character
            # 2. Add extra character
            # 3. Remove character
            choice = random.choice(["replace", "add", "remove"])
            
            if choice == "replace":
                noisy_text += random.choice(string.ascii_letters)
            elif choice == "add":
                noisy_text += char + random.choice(string.ascii_letters)
            else:
                continue
        else:
            noisy_text += char
    return noisy_text

def add_background_noise(text: str) -> str:
    """Simulate background noise in audio."""
    # Add random background sounds
    background_sounds = [
        "background_music",
        "keyboard_tapping",
        "people_talking",
        "environmental_noise"
    ]
    
    return f"{random.choice(background_sounds)} {text}"

def simulate_network_delay(text: str) -> str:
    """Simulate network delay."""
    import time
    delay = random.uniform(0.5, 2.0)  # Random delay between 0.5 and 2 seconds
    time.sleep(delay)
    return text

def simulate_api_failure(text: str) -> str:
    """Simulate API failure."""
    if random.random() < 0.5:  # 50% chance of failure
        raise Exception("Simulated API failure")
    return text

if __name__ == "__main__":
    pytest.main()
