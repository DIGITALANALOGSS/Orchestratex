"""
Tests for the PlannerAgent
"""

import pytest
from orchestratex.agents.planner_agent import PlannerAgent
from unittest.mock import MagicMock

class TestPlannerAgent:
    """Test cases for the PlannerAgent."""

    @pytest.fixture
    def mock_model(self):
        """Mock model fixture."""
        model = MagicMock()
        model.generate_plan = MagicMock(return_value=["Task 1", "Task 2"])
        return model

    @pytest.fixture
    def planner_agent(self, mock_model):
        """Planner agent fixture."""
        return PlannerAgent(
            name="Planner Agent",
            description="Decomposes complex tasks",
            tools=[],
            model=mock_model
        )

    def test_process_input(self, planner_agent, mock_model):
        """Test processing input."""
        result = planner_agent.process_input("Plan my day")
        assert result == ["Task 1", "Task 2"]
        mock_model.generate_plan.assert_called_once_with("Plan my day")

    def test_memory_tracking(self, planner_agent, mock_model):
        """Test memory tracking."""
        mock_model.generate_plan.return_value = ["Task 1", "Task 2"]
        planner_agent.process_input("Plan my day")
        assert len(planner_agent.memory) > 0
        assert "Plan: [\"Task 1\", \"Task 2\"]" in planner_agent.memory[0]

    def test_empty_input(self, planner_agent):
        """Test handling empty input."""
        mock_model = planner_agent.model
        mock_model.generate_plan.return_value = []
        result = planner_agent.process_input("")
        assert result == []
        mock_model.generate_plan.assert_called_once_with("")

    def test_large_input(self, planner_agent):
        """Test handling large input."""
        large_input = " " * 1000000
        mock_model = planner_agent.model
        mock_model.generate_plan.return_value = ["Task 1"]
        result = planner_agent.process_input(large_input)
        assert result == ["Task 1"]
        mock_model.generate_plan.assert_called_once_with(large_input)

    def test_error_handling(self, planner_agent):
        """Test error handling."""
        mock_model = planner_agent.model
        mock_model.generate_plan.side_effect = Exception("Model error")
        with pytest.raises(Exception):
            planner_agent.process_input("Test")
        assert len(planner_agent.memory) == 0
