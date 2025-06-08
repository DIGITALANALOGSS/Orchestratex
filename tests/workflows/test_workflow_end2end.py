"""
End-to-end tests for voice workflows
"""

import pytest
from orchestratex import run_workflow
from orchestratex.workflows import VoiceWorkflow

@pytest.mark.asyncio
async def test_multilingual_voice_workflow():
    """Test multilingual voice workflow end-to-end."""
    # Test English
    result = await run_workflow(
        name="voice_multilingual",
        input={"text": "Hello", "language": "en-US"}
    )
    assert result['output_language'] == "en-US"
    assert "Hello" in result['output_text']
    
    # Test Spanish
    result = await run_workflow(
        name="voice_multilingual",
        input={"text": "Hola", "language": "es-ES"}
    )
    assert result['output_language'] == "es-ES"
    assert "Hola" in result['output_text']
    
    # Test French
    result = await run_workflow(
        name="voice_multilingual",
        input={"text": "Bonjour", "language": "fr-FR"}
    )
    assert result['output_language'] == "fr-FR"
    assert "Bonjour" in result['output_text']

@pytest.mark.asyncio
async def test_voice_workflow_error_handling():
    """Test error handling in voice workflow."""
    # Test invalid language
    with pytest.raises(ValueError):
        await run_workflow(
            name="voice_multilingual",
            input={"text": "Hello", "language": "invalid-lang"}
        )
    
    # Test empty input
    with pytest.raises(ValueError):
        await run_workflow(
            name="voice_multilingual",
            input={"text": "", "language": "en-US"}
        )

@pytest.mark.asyncio
async def test_voice_workflow_performance():
    """Test voice workflow performance."""
    start_time = time.time()
    
    # Run multiple workflows in parallel
    workflows = [
        run_workflow(
            name="voice_multilingual",
            input={"text": "Hello", "language": "en-US"}
        ) for _ in range(10)
    ]
    
    results = await asyncio.gather(*workflows)
    
    duration = time.time() - start_time
    assert duration < 10  # Should complete in under 10 seconds
    
    # Verify all results
    for result in results:
        assert result['output_language'] == "en-US"
        assert "Hello" in result['output_text']

@pytest.mark.asyncio
async def test_voice_workflow_edge_cases():
    """Test voice workflow with edge cases."""
    # Test very short text
    result = await run_workflow(
        name="voice_multilingual",
        input={"text": ".", "language": "en-US"}
    )
    assert len(result['output_text']) > 0
    
    # Test special characters
    result = await run_workflow(
        name="voice_multilingual",
        input={"text": "!@#$%^&*()", "language": "en-US"}
    )
    assert len(result['output_text']) > 0
