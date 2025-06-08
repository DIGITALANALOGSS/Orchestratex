import pytest
from orchestratex.models import rag_maestro
from orchestratex.config import get_settings
import numpy as np

@pytest.mark.parametrize("noise_level", [0, 0.1, 0.5, 0.9])
def test_rag_with_noise(noise_level):
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Add noise to input
    query = "What is AI?"
    noisy_query = add_typographical_noise(query, noise_level)
    
    response = model.query(noisy_query)
    assert response is not None and len(response) > 0
    assert "artificial intelligence" in response.lower()

def test_model_explainability():
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Test explainability
    explanation = model.explain("Why did you answer X?", context="AI is changing the world")
    assert "because" in explanation.lower()
    assert "context" in explanation.lower()
    assert "retrieval" in explanation.lower()

def test_model_multilingual_support():
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Test multiple languages
    languages = ["en-US", "es-ES", "fr-FR", "de-DE"]
    for lang in languages:
        response = model.query("What is AI?", language=lang)
        assert response is not None and len(response) > 0
        assert response != ""

def test_model_context_handling():
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Test with and without context
    context = "AI has revolutionized many industries"
    
    response_with_context = model.query("What has AI done?", context=context)
    response_without_context = model.query("What has AI done?")
    
    assert response_with_context != response_without_context
    assert context.lower() in response_with_context.lower()

def test_model_error_handling():
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Test invalid inputs
    with pytest.raises(ValueError):
        model.query(None)
    
    with pytest.raises(ValueError):
        model.query("")
    
    with pytest.raises(ValueError):
        model.query("a" * 5000)  # Too long input

def test_model_performance():
    settings = get_settings()
    model = rag_maestro(settings)
    
    # Test response time
    import time
    start = time.time()
    for _ in range(10):
        model.query("What is AI?")
    duration = time.time() - start
    
    assert duration < 5, "Model response time too slow"

def add_typographical_noise(text: str, noise_level: float) -> str:
    """Add typographical noise to text."""
    if noise_level == 0:
        return text
    
    noisy_text = ""
    for char in text:
        if np.random.random() < noise_level:
            # Randomly choose between:
            # 1. Replace with random character
            # 2. Add extra character
            # 3. Remove character
            choice = np.random.choice(["replace", "add", "remove"])
            
            if choice == "replace":
                noisy_text += chr(np.random.randint(32, 127))
            elif choice == "add":
                noisy_text += char + chr(np.random.randint(32, 127))
            else:
                continue
        else:
            noisy_text += char
    
    return noisy_text

if __name__ == "__main__":
    pytest.main()
