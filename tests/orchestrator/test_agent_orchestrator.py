"""
Tests for the AgentOrchestrator
"""

import pytest
from orchestratex.orchestrator import AgentOrchestrator
from orchestratex.agents.planner_agent import PlannerAgent
from orchestratex.agents.rag_maestro import RAGMaestro
from orchestratex.agents.code_agent import CodeAgent
from orchestratex.agents.voice_agent import VoiceAgent
from orchestratex.tools.weather_tool import WeatherTool
from orchestratex.tools.time_tool import TimeTool
from unittest.mock import MagicMock

class TestAgentOrchestrator:
    """Test cases for the AgentOrchestrator."""

    @pytest.fixture
    def mock_model(self):
        """Mock model fixture."""
        model = MagicMock()
        model.generate_plan = MagicMock(return_value="Mock plan")
        model.retrieve = MagicMock(return_value="Mock context")
        model.generate_code = MagicMock(return_value="Mock code")
        model.transcribe = MagicMock(return_value="Mock transcript")
        model.synthesize = MagicMock(return_value="Mock response")
        return model

    @pytest.fixture
    def agents(self, mock_model):
        """Agents fixture."""
        planner = PlannerAgent("Planner Agent", "Decomposes tasks", [], mock_model)
        rag = RAGMaestro("RAG Agent", "Retrieves knowledge", [], mock_model)
        code = CodeAgent("Code Agent", "Writes code", [], mock_model)
        voice = VoiceAgent("Voice Agent", "Handles voice", [], mock_model)
        weather_agent = PlannerAgent("Weather Agent", "Handles weather", [WeatherTool()], mock_model)
        time_agent = PlannerAgent("Time Agent", "Handles time", [TimeTool()], mock_model)
        return [planner, rag, code, voice, weather_agent, time_agent]

    @pytest.fixture
    def orchestrator(self, agents):
        """Orchestrator fixture."""
        return AgentOrchestrator(agents)

    def test_initialization(self, orchestrator, agents):
        """Test orchestrator initialization."""
        assert len(orchestrator.agents) == len(agents)
        assert hasattr(orchestrator, "memory")
        assert isinstance(orchestrator.memory, list)

    def test_orchestrate_task_weather(self, orchestrator):
        """Test weather task orchestration."""
        result = orchestrator.orchestrate_task("What's the weather in Bangalore?")
        assert "Weather" in result
        assert "Bangalore" in result

    def test_orchestrate_task_time(self, orchestrator):
        """Test time task orchestration."""
        result = orchestrator.orchestrate_task("What time is it in New York?")
        assert "Current time" in result
        assert "New York" in result

    def test_orchestrate_task_code(self, orchestrator):
        """Test code task orchestration."""
        result = orchestrator.orchestrate_task("Write a Python function")
        assert "Mock code" in result

    def test_orchestrate_task_voice(self, orchestrator):
        """Test voice task orchestration."""
        result = orchestrator.orchestrate_task("Say hello")
        assert "Mock response" in result

    def test_orchestrate_task_planner(self, orchestrator):
        """Test planner task orchestration."""
        result = orchestrator.orchestrate_task("Plan my day")
        assert "Mock plan" in result

    def test_orchestrate_task_no_agent(self, orchestrator):
        """Test task with no matching agent."""
        result = orchestrator.orchestrate_task("Invalid task")
        assert "No suitable agent found" in result

    def test_memory_tracking(self, orchestrator):
        """Test memory tracking."""
        orchestrator.orchestrate_task("Plan my day")
        assert len(orchestrator.memory) > 0
        assert "Planner Agent" in orchestrator.memory[0]

    def test_invalid_input(self, orchestrator):
        """Test invalid input handling."""
        result = orchestrator.orchestrate_task(None)
        assert "No suitable agent found" in result

    def test_empty_input(self, orchestrator):
        """Test empty input handling."""
        result = orchestrator.orchestrate_task("")
        assert "No suitable agent found" in result
