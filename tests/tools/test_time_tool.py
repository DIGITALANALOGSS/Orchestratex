"""
Tests for the TimeTool
"""

import pytest
from orchestratex.tools.time_tool import TimeTool
from datetime import datetime
import pytz

class TestTimeTool:
    """Test cases for the TimeTool."""

    @pytest.fixture
    def time_tool(self):
        """Time tool fixture."""
        return TimeTool()

    def test_name(self, time_tool):
        """Test tool name."""
        assert time_tool.name() == "Time Tool"

    def test_description(self, time_tool):
        """Test tool description."""
        assert time_tool.description() == "Provides the current time for a given city."

    def test_use_valid_city(self, time_tool, monkeypatch):
        """Test getting time for valid cities."""
        # Test Bangalore
        monkeypatch.setattr(
            datetime,
            'now',
            lambda tz: datetime(2025, 6, 6, 18, 34, 0, tzinfo=tz)
        )
        result = time_tool.use("Bangalore")
        assert result == "Current time in Bangalore is 21:34 PM."

        # Test New York
        result = time_tool.use("New York")
        assert result == "Current time in New York is 18:34 PM."

    def test_use_invalid_city(self, time_tool):
        """Test getting time for invalid city."""
        result = time_tool.use("InvalidCity")
        assert result == "Current time in InvalidCity is 18:34 PM."

    def test_timezone_mapping(self, time_tool):
        """Test timezone mapping."""
        assert time_tool.use("Bangalore") == "Current time in Bangalore is 21:34 PM."
        assert time_tool.use("New York") == "Current time in New York is 18:34 PM."
        assert time_tool.use("Unknown") == "Current time in Unknown is 18:34 PM."

    def test_time_formatting(self, time_tool, monkeypatch):
        """Test time formatting."""
        monkeypatch.setattr(
            datetime,
            'now',
            lambda tz: datetime(2025, 6, 6, 0, 34, 0, tzinfo=tz)
        )
        result = time_tool.use("Bangalore")
        assert result == "Current time in Bangalore is 03:34 AM."

    def test_edge_cases(self, time_tool, monkeypatch):
        """Test edge cases."""
        # Test midnight
        monkeypatch.setattr(
            datetime,
            'now',
            lambda tz: datetime(2025, 6, 6, 0, 0, 0, tzinfo=tz)
        )
        result = time_tool.use("Bangalore")
        assert result == "Current time in Bangalore is 03:00 AM."

        # Test noon
        monkeypatch.setattr(
            datetime,
            'now',
            lambda tz: datetime(2025, 6, 6, 12, 0, 0, tzinfo=tz)
        )
        result = time_tool.use("Bangalore")
        assert result == "Current time in Bangalore is 15:00 PM."
