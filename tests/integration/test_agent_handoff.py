import pytest
from orchestratex.agents import planner, rag_maestro, voice_agent
from orchestratex.workflow import WorkflowManager
from orchestratex.config import get_settings

@pytest.fixture
def workflow_manager():
    settings = get_settings()
    return WorkflowManager(settings)

@pytest.mark.parametrize("task", [
    "translate and summarize",
    "analyze sentiment",
    "generate response",
    "extract key points"
])
def test_agent_handoff(task, workflow_manager):
    input_data = {
        "task": task,
        "text": "AI is changing the world. It's revolutionizing industries and creating new opportunities.",
        "language": "en-US",
        "target_language": "es-ES"
    }
    
    result = workflow_manager.run_workflow("agent_handoff", input_data)
    
    assert result is not None
    assert "agents_involved" in result
    assert "output" in result
    
    # Verify correct agents were involved
    expected_agents = ["planner", "rag_maestro", "voice_agent"]
    for agent in expected_agents:
        assert agent in result["agents_involved"]
    
    # Verify output quality
    if task == "translate and summarize":
        assert len(result["output"]) > 0
        assert result["output_language"] == "es-ES"
    elif task == "analyze sentiment":
        assert "sentiment" in result["output"]
        assert "confidence" in result["output"]
    elif task == "generate response":
        assert len(result["output"]) > 0
        assert result["output_language"] == "en-US"
    elif task == "extract key points":
        assert isinstance(result["output"], list)
        assert len(result["output"]) > 0

@pytest.mark.parametrize("language_pair", [
    ("en-US", "es-ES"),
    ("es-ES", "en-US"),
    ("fr-FR", "de-DE")
])
def test_multilingual_handoff(language_pair, workflow_manager):
    src_lang, tgt_lang = language_pair
    input_data = {
        "task": "translate",
        "text": "Bonjour, comment ça va?",  # French input
        "source_language": src_lang,
        "target_language": tgt_lang
    }
    
    result = workflow_manager.run_workflow("translate_workflow", input_data)
    
    assert result["output_language"] == tgt_lang
    assert len(result["output"]) > 0
    assert result["confidence"] > 0.5

@pytest.mark.parametrize("error_type", [
    "invalid_language",
    "missing_input",
    "invalid_task",
    "api_failure"
])
def test_error_handling(error_type, workflow_manager, monkeypatch):
    input_data = {
        "task": "translate",
        "text": "Hello",
        "source_language": "en-US",
        "target_language": "en-US"
    }
    
    if error_type == "invalid_language":
        input_data["target_language"] = "invalid-lang"
    elif error_type == "missing_input":
        input_data["text"] = ""
    elif error_type == "invalid_task":
        input_data["task"] = "invalid_task"
    elif error_type == "api_failure":
        def fail_api(*args, **kwargs):
            raise Exception("Simulated API failure")
        monkeypatch.setattr(voice_agent, "transcribe", fail_api)
    
    with pytest.raises(Exception) as e:
        workflow_manager.run_workflow("translate_workflow", input_data)
    
    assert error_type in str(e.value).lower()

@pytest.mark.parametrize("concurrent_requests", [1, 5, 10])
def test_concurrent_handoff(concurrent_requests, workflow_manager):
    import concurrent.futures
    import time
    
    input_data = {
        "task": "translate",
        "text": "Hello",
        "source_language": "en-US",
        "target_language": "es-ES"
    }
    
    start_time = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(
            workflow_manager.run_workflow,
            "translate_workflow",
            input_data
        ) for _ in range(concurrent_requests)]
        
        results = concurrent.futures.wait(futures)
        
    duration = time.time() - start_time
    
    assert len(results.done) == concurrent_requests
    assert duration < 30  # Should complete within 30 seconds
    
    for future in results.done:
        result = future.result()
        assert result is not None
        assert result["output_language"] == "es-ES"

if __name__ == "__main__":
    pytest.main()
