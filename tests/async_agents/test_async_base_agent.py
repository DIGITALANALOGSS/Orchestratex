"""
Tests for the AsyncAgent base class
"""

import pytest
import asyncio
from orchestratex.async_agents.base_agent import AsyncAgent
from unittest.mock import AsyncMock, MagicMock

class TestAsyncBaseAgent:
    """Test cases for the AsyncAgent base class."""

    @pytest.fixture
    def mock_model(self):
        """Mock model fixture."""
        model = AsyncMock()
        model.generate_plan = AsyncMock(return_value="Mock plan")
        model.retrieve = AsyncMock(return_value="Mock context")
        model.generate_code = AsyncMock(return_value="Mock code")
        model.transcribe = AsyncMock(return_value="Mock transcript")
        model.synthesize = AsyncMock(return_value="Mock response")
        return model

    @pytest.fixture
    def async_agent(self, mock_model):
        """Async agent fixture."""
        return AsyncAgent(
            name="Async Agent",
            description="Async agent description",
            tools=[],
            model=mock_model
        )

    @pytest.mark.asyncio
    async def test_initialization(self, async_agent):
        """Test agent initialization."""
        assert async_agent.name == "Async Agent"
        assert async_agent.description == "Async agent description"
        assert async_agent.tools == []
        assert hasattr(async_agent, "memory")
        assert isinstance(async_agent.memory, list)

    @pytest.mark.asyncio
    async def test_send_message(self, async_agent):
        """Test async message sending."""
        target_agent = AsyncAgent("Target", "Target agent", [], None)
        await async_agent.send_message(target_agent, "Test message")
        assert "Received: Test message" in target_agent.memory

    @pytest.mark.asyncio
    async def test_receive_message(self, async_agent):
        """Test async message receiving."""
        await async_agent.receive_message("Test message")
        assert "Received: Test message" in async_agent.memory

    @pytest.mark.asyncio
    async def test_concurrent_messages(self, async_agent):
        """Test concurrent message handling."""
        messages = ["Message 1", "Message 2", "Message 3"]
        tasks = [async_agent.receive_message(msg) for msg in messages]
        await asyncio.gather(*tasks)
        assert len(async_agent.memory) == 3
        for msg in messages:
            assert f"Received: {msg}" in async_agent.memory

    @pytest.mark.asyncio
    async def test_error_handling(self, async_agent):
        """Test error handling in async operations."""
        target_agent = AsyncAgent("Target", "Target agent", [], None)
        
        # Test sending message to None
        with pytest.raises(AttributeError):
            await async_agent.send_message(None, "Test message")

        # Test sending message to invalid agent
        invalid_agent = MagicMock()
        with pytest.raises(AttributeError):
            await async_agent.send_message(invalid_agent, "Test message")
