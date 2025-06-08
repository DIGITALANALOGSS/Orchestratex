"""
Tests for the base Agent class
"""

import pytest
from orchestratex.agents.base_agent import Agent
from unittest.mock import MagicMock

class TestBaseAgent:
    """Test cases for the base Agent class."""

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
    def base_agent(self, mock_model):
        """Base agent fixture."""
        return Agent(
            name="Test Agent",
            description="Test agent description",
            tools=[],
            model=mock_model
        )

    def test_initialization(self, base_agent):
        """Test agent initialization."""
        assert base_agent.name == "Test Agent"
        assert base_agent.description == "Test agent description"
        assert base_agent.tools == []
        assert hasattr(base_agent, "memory")
        assert isinstance(base_agent.memory, list)

    def test_json_parser_valid_json(self, base_agent):
        """Test JSON parsing with valid JSON."""
        valid_json = '{"key": "value"}'
        result = base_agent.json_parser(valid_json)
        assert result == {"key": "value"}

    def test_json_parser_invalid_json(self, base_agent):
        """Test JSON parsing with invalid JSON (fallback to eval)."""
        invalid_json = "{'key': 'value'}"  # Single quotes
        result = base_agent.json_parser(invalid_json)
        assert result == {"key": "value"}

    def test_json_parser_eval_error(self, base_agent):
        """Test JSON parsing with invalid input that fails eval."""
        invalid_input = "invalid syntax"
        with pytest.raises(ValueError):
            base_agent.json_parser(invalid_input)

    def test_memory_tracking(self, base_agent, mock_model):
        """Test memory tracking."""
        mock_model.generate_plan.return_value = "Plan 1"
        base_agent.process_input("test input")
        assert len(base_agent.memory) > 0
        assert "Plan 1" in base_agent.memory[0]
