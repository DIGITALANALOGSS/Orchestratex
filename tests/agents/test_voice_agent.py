import pytest
from orchestratex.agents import VoiceAgent
from unittest.mock import patch, MagicMock
from orchestratex.config import get_settings
from orchestratex.exceptions import VoiceAgentError
from orchestratex.metrics import metrics
import numpy as np

# Mock settings for testing
@pytest.fixture
def mock_settings():
    settings = get_settings()
    settings.GOOGLE_APPLICATION_CREDENTIALS = "mock_credentials.json"
    settings.VOICE_AGENT_MAX_RETRIES = 3
    settings.VOICE_AGENT_RETRY_DELAY = 1.5
    settings.VOICE_AGENT_TIMEOUT = 10
    return settings

# Mock voice agent instance
@pytest.fixture
def voice_agent(mock_settings):
    return VoiceAgent(mock_settings)

# Mock settings for testing
@pytest.fixture
def mock_settings():
    settings = get_settings()
    settings.GOOGLE_APPLICATION_CREDENTIALS = "mock_credentials.json"
    settings.VOICE_AGENT_MAX_RETRIES = 3
    settings.VOICE_AGENT_RETRY_DELAY = 1.5
    settings.VOICE_AGENT_TIMEOUT = 10
    return settings

# Mock voice agent instance
@pytest.fixture
def voice_agent(mock_settings):
    return VoiceAgent(mock_settings)

# Test basic initialization
def test_voice_agent_initialization(mock_settings):
    agent = VoiceAgent(mock_settings)
    assert agent.settings == mock_settings
    assert agent.metrics == metrics
    assert agent._client is None
    assert agent._tts_client is None

@pytest.mark.parametrize("language,text,expected", [
    ("en-US", "Hello", "Hello"),
    ("es-ES", "Hola", "Hola"),
    ("zh-CN", "你好", "你好"),
    ("fr-FR", "Bonjour", "Bonjour"),
    ("de-DE", "Hallo", "Hallo")
])
def test_voice_agent_multilingual(language, text, expected, voice_agent):
    """Test voice agent's multilingual support."""
    with patch('google.cloud.texttospeech_v1.TextToSpeechClient') as mock_tts:
        mock_tts_instance = mock_tts.return_value
        mock_tts_instance.synthesize_speech.return_value = MagicMock(audio_content=b'mock_audio')
        
        # Mock transcription
        with patch('google.cloud.speech_v1p1beta1.SpeechClient') as mock_speech:
            mock_speech_instance = mock_speech.return_value
            mock_speech_instance.recognize.return_value = MagicMock(
                results=[MagicMock(
                    alternatives=[MagicMock(
                        transcript=expected
                    )]
                )]
            )
            
            # Test synthesis and transcription
            audio = voice_agent.synthesize_speech(text, language_code=language)
            assert isinstance(audio, bytes)
            
            # Test transcription
            transcription = voice_agent.transcribe_audio(audio, language_code=language)
            assert expected in transcription[0]["transcript"]


def test_voice_agent_error_handling(voice_agent):
    """Test voice agent's error handling."""
    # Test empty input
    with pytest.raises(ValueError):
        voice_agent.synthesize_speech("")
    
    # Test invalid language code
    with pytest.raises(ValueError):
        voice_agent.synthesize_speech("test", language_code="invalid-code")
    
    # Test API error
    with patch('google.cloud.texttospeech_v1.TextToSpeechClient') as mock_tts:
        mock_tts_instance = mock_tts.return_value
        mock_tts_instance.synthesize_speech.side_effect = Exception("API Error")
        
        with pytest.raises(VoiceAgentError):
            voice_agent.synthesize_speech("test", language_code="en-US")

def test_voice_agent_adaptive_retries(voice_agent, monkeypatch):
    """Test voice agent's adaptive retry mechanism."""
    call_count = {"count": 0}
    
    def fail_once(*args, **kwargs):
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise Exception("Simulated failure")
        return MagicMock(audio_content=b'mock_audio')
    
    monkeypatch.setattr(voice_agent, "synthesize_speech", fail_once)
    
    # First call should fail, second should succeed
    result = voice_agent.synthesize_speech("Test", language_code="en-US")
    assert result == b'mock_audio'
    assert call_count["count"] == 2  # Should have retried once

# Test language validation
@pytest.mark.parametrize("language", [
    "en-US",
    "es-ES",
    "fr-FR",
    "de-DE",
    "it-IT",
    "pt-PT",
    "nl-NL",
    "sv-SE",
    "fi-FI",
    "da-DK",
    "no-NO",
    "pl-PL"
])
def test_valid_language_validation(voice_agent, language):
    assert voice_agent._validate_language(language) == True

@pytest.mark.parametrize("invalid_language", [
    "en",
    "invalid-code",
    "not-a-language",
    "123"
])
def test_invalid_language_validation(voice_agent, invalid_language):
    assert voice_agent._validate_language(invalid_language) == False

# Performance test
def test_voice_agent_performance(voice_agent):
    """Test voice agent's performance with large input."""
    start_time = time.time()
    
    # Generate large text (1000 characters)
    large_text = " ".join(["test"] * 1000)
    
    # Synthesize and transcribe
    audio = voice_agent.synthesize_speech(large_text, language_code="en-US")
    transcription = voice_agent.transcribe_audio(audio, language_code="en-US")
    
    duration = time.time() - start_time
    assert duration < 10  # Should complete in under 10 seconds

# Security test
def test_voice_agent_security(voice_agent):
    """Test voice agent's security features."""
    # Test injection attempts
    malicious_text = "__import__('os').system('rm -rf /')"
    with pytest.raises(ValueError):
        voice_agent.synthesize_speech(malicious_text)
    
    # Test large input protection
    with pytest.raises(ValueError):
        voice_agent.synthesize_speech("a" * 1000000)  # 1MB input

# Edge case test
def test_voice_agent_edge_cases(voice_agent):
    """Test voice agent with edge cases."""
    # Test very short text
    audio = voice_agent.synthesize_speech(".", language_code="en-US")
    assert len(audio) > 0
    
    # Test special characters
    text_with_special_chars = "!@#$%^&*()"
    audio = voice_agent.synthesize_speech(text_with_special_chars, language_code="en-US")
    assert len(audio) > 0
    "invalid-lang",
    "es-ES-variant",
    "fr",
    ""
])
def test_invalid_language_validation(voice_agent, invalid_language):
    with pytest.raises(VoiceAgentError):
        voice_agent._validate_language(invalid_language)

# Test audio processing
@patch('google.cloud.speech_v1.SpeechClient')
@patch('google.cloud.texttospeech_v1.TextToSpeechClient')
def test_process_audio_success(mock_tts_client, mock_speech_client, voice_agent):
    # Mock response
    mock_response = MagicMock()
    mock_response.results = [MagicMock(alternatives=[MagicMock(
        transcript="Hello",
        confidence=0.95
    )])]
    
    mock_speech_client.return_value.recognize.return_value = mock_response
    
    result = voice_agent.process_audio(b"mock_audio", "en-US")
    
    assert result == "Hello"
    assert metrics.voice_agent_audio_quality.labels(language="en-US")._value.get() == 0.95

@patch('google.cloud.speech_v1.SpeechClient')
def test_process_audio_failure(mock_speech_client, voice_agent):
    mock_speech_client.return_value.recognize.side_effect = Exception("API Error")
    
    with pytest.raises(VoiceAgentError):
        voice_agent.process_audio(b"mock_audio", "en-US")
    
    assert metrics.voice_agent_errors.labels(
        operation="process_audio",
        language="en-US",
        error_type="api_error",
        cause="API Error"
    )._value.get() > 0

# Test emotion detection
@pytest.mark.parametrize("text, expected_emotions", [
    ("I'm really happy today!", {"happiness": 0.9, "sadness": 0.1, "neutral": 0.05}),
    ("This is terrible news.", {"sadness": 0.8, "anger": 0.2, "neutral": 0.1}),
    ("I'm surprised!", {"surprise": 0.7, "neutral": 0.3})
])
def test_emotion_detection(voice_agent, text, expected_emotions):
    with patch.object(voice_agent, '_detect_emotion', return_value=expected_emotions):
        result = voice_agent.detect_emotion(text)
        assert result == expected_emotions
        
        # Verify metrics
        for emotion, value in expected_emotions.items():
            assert metrics.voice_agent_emotion_confidence.labels(
                emotion=emotion,
                language="en-US"
            )._value.get() == value

# Test retry mechanism
@patch('google.cloud.speech_v1.SpeechClient')
def test_retry_mechanism(mock_speech_client, voice_agent):
    # First two attempts fail, third succeeds
    mock_responses = [
        Exception("API Error"),
        Exception("API Error"),
        MagicMock(results=[MagicMock(alternatives=[MagicMock(
            transcript="Hello",
            confidence=0.95
        )])])
    ]
    
    mock_speech_client.return_value.recognize.side_effect = mock_responses
    
    result = voice_agent.process_audio(b"mock_audio", "en-US")
    assert result == "Hello"
    assert mock_speech_client.return_value.recognize.call_count == 3

# Test queue management
@pytest.mark.parametrize("queue_size", [0, 1, 5, 10])
def test_queue_management(voice_agent, queue_size):
    # Add items to queue
    for i in range(queue_size):
        voice_agent._add_to_queue({"id": i, "data": f"item_{i}"})
    
    assert len(voice_agent._queue) == queue_size
    
    # Process queue
    for i in range(queue_size):
        item = voice_agent._get_from_queue()
        assert item["id"] == i
        assert item["data"] == f"item_{i}"

# Test error handling
@pytest.mark.parametrize("error_type", [
    "invalid_language",
    "audio_processing",
    "network",
    "authentication",
    "api_error"
])
def test_error_handling(voice_agent, error_type):
    with patch.object(voice_agent, '_process_audio', side_effect=Exception(f"{error_type} error")):
        try:
            voice_agent.process_audio(b"mock_audio", "en-US")
        except VoiceAgentError as e:
            assert error_type in str(e)
            assert metrics.voice_agent_errors.labels(
                operation="process_audio",
                language="en-US",
                error_type=error_type,
                cause=str(e)
            )._value.get() > 0

if __name__ == "__main__":
    unittest.main()
