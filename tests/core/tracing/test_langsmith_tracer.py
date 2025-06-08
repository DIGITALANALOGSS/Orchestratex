"""
Tests for LangSmithTracer
"""

import pytest
import asyncio
from orchestratex.core.tracing import LangSmithTracer, MockLangSmithClient

class TestLangSmithTracer:
    """Test cases for LangSmithTracer."""

    @pytest.fixture
    def tracer(self):
        """LangSmith tracer fixture."""
        return LangSmithTracer(api_key="test_key")

    @pytest.fixture
    def mock_client(self):
        """Mock LangSmith client fixture."""
        return MockLangSmithClient()

    @pytest.mark.asyncio
    async def test_trace_decorator(self, tracer):
        """Test trace decorator functionality."""
        @tracer.trace("test_agent")
        async def test_function():
            return "success"

        # Test successful execution
        result = await test_function()
        assert result == "success"

        # Test error handling
        @tracer.trace("error_agent")
        async def error_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            await error_function()

    @pytest.mark.asyncio
    async def test_concurrent_traces(self, tracer):
        """Test concurrent tracing."""
        @tracer.trace("concurrent_agent")
        async def concurrent_function():
            await asyncio.sleep(0.1)
            return "success"

        # Run multiple concurrent functions
        tasks = [concurrent_function() for _ in range(3)]
        results = await asyncio.gather(*tasks)
        assert all(result == "success" for result in results)

    @pytest.mark.asyncio
    async def test_nested_traces(self, tracer):
        """Test nested tracing."""
        @tracer.trace("outer_agent")
        async def outer_function():
            @tracer.trace("inner_agent")
            async def inner_function():
                return "inner success"
            
            inner_result = await inner_function()
            return f"outer success with {inner_result}"

        result = await outer_function()
        assert result == "outer success with inner success"

    @pytest.mark.asyncio
    async def test_custom_data_logging(self, tracer):
        """Test custom data logging in traces."""
        @tracer.trace("data_agent")
        async def data_function():
            return {"key": "value", "number": 42}

        result = await data_function()
        assert isinstance(result, dict)
        assert "key" in result
        assert "number" in result
