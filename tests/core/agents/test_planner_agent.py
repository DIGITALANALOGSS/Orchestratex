"""
Tests for PlannerAgent
"""

import pytest
import asyncio
from orchestratex.core.agents.planner_agent import PlannerAgent
from unittest.mock import AsyncMock, MagicMock

class TestPlannerAgent:
    """Test cases for PlannerAgent."""

    @pytest.fixture
    def mock_tool(self):
        """Mock tool fixture."""
        tool = MagicMock()
        tool.name = "MockTool"
        return tool

    @pytest.fixture
    def planner_agent(self, mock_tool):
        """Planner agent fixture."""
        return PlannerAgent(tools=[mock_tool])

    @pytest.mark.asyncio
    async def test_decompose_task(self, planner_agent):
        """Test task decomposition."""
        # Test with a complex task
        result = await planner_agent.decompose_task({"task": "Build weather dashboard"})
        assert "subtasks" in result
        assert len(result["subtasks"]) > 0

    @pytest.mark.asyncio
    async def test_workflow_execution(self, planner_agent):
        """Test complete workflow execution."""
        input_data = {
            "task": "Build weather dashboard",
            "parameters": {
                "location": "London",
                "features": ["temperature", "humidity", "forecast"]
            }
        }
        
        result = await planner_agent.process(input_data)
        assert "subtasks" in result
        assert len(result["subtasks"]) > 0
        
        # Verify subtasks are structured correctly
        for subtask in result["subtasks"]:
            assert "name" in subtask
            assert "description" in subtask
            assert "dependencies" in subtask

    @pytest.mark.asyncio
    async def test_error_handling(self, planner_agent):
        """Test error handling in workflow."""
        # Test invalid input
        with pytest.raises(Exception):
            await planner_agent.process({"invalid": "data"})

    @pytest.mark.asyncio
    async def test_parallel_execution(self, planner_agent):
        """Test parallel task execution."""
        input_data = {
            "task": "Build weather dashboard",
            "parameters": {
                "locations": ["London", "Paris", "Berlin"]
            }
        }
        
        result = await planner_agent.process(input_data)
        assert "subtasks" in result
        assert len(result["subtasks"]) > 0
        
        # Verify parallel tasks are created
        location_tasks = [t for t in result["subtasks"] if "location" in t["description"]]
        assert len(location_tasks) == 3

    @pytest.mark.asyncio
    async def test_conditional_routing(self, planner_agent):
        """Test conditional workflow routing."""
        input_data = {
            "task": "Build weather dashboard",
            "parameters": {
                "features": ["temperature", "humidity"]
            }
        }
        
        result = await planner_agent.process(input_data)
        assert "subtasks" in result
        
        # Verify only relevant subtasks are created
        feature_tasks = [t for t in result["subtasks"] if "temperature" in t["description"] or "humidity" in t["description"]]
        assert len(feature_tasks) > 0
