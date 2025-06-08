"""
Tests for the CodeAgent
"""

import pytest
from orchestratex.agents.code_agent import CodeAgent
from unittest.mock import MagicMock

class TestCodeAgent:
    """Test cases for the CodeAgent."""

    @pytest.fixture
    def mock_model(self):
        """Mock model fixture."""
        model = MagicMock()
        model.generate_code = MagicMock(return_value="def hello(): print('Hello')")
        return model

    @pytest.fixture
    def code_agent(self, mock_model):
        """Code agent fixture."""
        return CodeAgent(
            name="Code Agent",
            description="Generates, reviews, and refactors code",
            tools=[],
            model=mock_model
        )

    def test_process_input(self, code_agent, mock_model):
        """Test processing input."""
        result = code_agent.process_input("Write a hello world function")
        assert result == "def hello(): print('Hello')"
        mock_model.generate_code.assert_called_once_with("Write a hello world function")

    def test_memory_tracking(self, code_agent, mock_model):
        """Test memory tracking."""
        mock_model.generate_code.return_value = "def hello(): print('Hello')"
        code_agent.process_input("Write a hello world function")
        assert len(code_agent.memory) > 0
        assert "Code: def hello(): print('Hello')" in code_agent.memory[0]

    def test_empty_input(self, code_agent):
        """Test handling empty input."""
        mock_model = code_agent.model
        mock_model.generate_code.return_value = ""
        result = code_agent.process_input("")
        assert result == ""
        mock_model.generate_code.assert_called_once_with("")

    def test_large_input(self, code_agent):
        """Test handling large input."""
        large_input = " " * 1000000
        mock_model = code_agent.model
        mock_model.generate_code.return_value = "def func(): pass"
        result = code_agent.process_input(large_input)
        assert result == "def func(): pass"
        mock_model.generate_code.assert_called_once_with(large_input)

    def test_error_handling(self, code_agent):
        """Test error handling."""
        mock_model = code_agent.model
        mock_model.generate_code.side_effect = Exception("Code generation error")
        with pytest.raises(Exception):
            code_agent.process_input("Test")
        assert len(code_agent.memory) == 0
