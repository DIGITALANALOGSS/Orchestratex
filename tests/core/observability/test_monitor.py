"""
Tests for AgentMonitor
"""

import pytest
from orchestratex.core.observability.monitoring import AgentMonitor
from unittest.mock import AsyncMock, MagicMock

class TestAgentMonitor:
    """Test cases for AgentMonitor."""

    @pytest.fixture
    def agent_monitor(self):
        """Agent monitor fixture."""
        return AgentMonitor(port=9090)

    @pytest.mark.asyncio
    async def test_metrics_tracking(self, agent_monitor):
        """Test metrics tracking."""
        # Mock a decorated function
        @agent_monitor.track_metrics("test_agent")
        async def test_function():
            return "success"

        # Call the function multiple times
        for _ in range(3):
            await test_function()

        # Verify request count
        assert agent_monitor.REQUEST_COUNT.labels(agent="test_agent")._value.get() == 3

    @pytest.mark.asyncio
    async def test_error_tracking(self, agent_monitor):
        """Test error tracking."""
        # Mock a decorated function that raises an error
        @agent_monitor.track_metrics("error_agent")
        async def error_function():
            raise Exception("Test error")

        try:
            await error_function()
        except Exception:
            pass

        # Verify error count
        assert agent_monitor.ERROR_COUNT.labels(agent="error_agent")._value.get() == 1

    @pytest.mark.asyncio
    async def test_processing_time(self, agent_monitor):
        """Test processing time tracking."""
        # Mock a decorated function with controlled processing time
        @agent_monitor.track_metrics("time_agent")
        async def time_function():
            await asyncio.sleep(0.1)
            return "success"

        await time_function()

        # Verify processing time histogram
        samples = list(agent_monitor.PROCESSING_TIME.collect()[0].samples)
        assert len(samples) > 0
        assert samples[0].value >= 0.1

    @pytest.mark.asyncio
    async def test_multiple_agents(self, agent_monitor):
        """Test metrics tracking for multiple agents."""
        # Create decorated functions for different agents
        @agent_monitor.track_metrics("agent1")
        async def agent1_function():
            return "success"

        @agent_monitor.track_metrics("agent2")
        async def agent2_function():
            return "success"

        # Call each function
        await agent1_function()
        await agent2_function()

        # Verify metrics for each agent
        assert agent_monitor.REQUEST_COUNT.labels(agent="agent1")._value.get() == 1
        assert agent_monitor.REQUEST_COUNT.labels(agent="agent2")._value.get() == 1

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, agent_monitor):
        """Test concurrent request tracking."""
        # Create decorated function
        @agent_monitor.track_metrics("concurrent_agent")
        async def concurrent_function():
            await asyncio.sleep(0.1)
            return "success"

        # Run multiple concurrent requests
        tasks = [concurrent_function() for _ in range(5)]
        await asyncio.gather(*tasks)

        # Verify metrics
        assert agent_monitor.REQUEST_COUNT.labels(agent="concurrent_agent")._value.get() == 5
        samples = list(agent_monitor.PROCESSING_TIME.collect()[0].samples)
        assert len(samples) > 0
