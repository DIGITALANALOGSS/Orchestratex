"""
Tests for the WeatherTool
"""

import pytest
import os
from orchestratex.tools.weather_tool import WeatherTool
from unittest.mock import patch, MagicMock

class TestWeatherTool:
    """Test cases for the WeatherTool."""

    @pytest.fixture
    def weather_tool(self):
        """Weather tool fixture."""
        return WeatherTool()

    def test_name(self, weather_tool):
        """Test tool name."""
        assert weather_tool.name() == "Weather Tool"

    def test_description(self, weather_tool):
        """Test tool description."""
        assert weather_tool.description() == "Provides weather information for a given location."

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_api_key"})
    @patch('requests.get')
    def test_use_success(self, mock_get, weather_tool):
        """Test successful weather lookup."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "cod": 200,
            "main": {"temp": 25},
            "weather": [{"description": "sunny"}]
        }
        mock_get.return_value = mock_response

        result = weather_tool.use("Bangalore")
        assert result == "Weather in Bangalore: sunny, 25°C."
        mock_get.assert_called_once()

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_api_key"})
    @patch('requests.get')
    def test_use_failure(self, mock_get, weather_tool):
        """Test failed weather lookup."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"cod": 404}
        mock_get.return_value = mock_response

        result = weather_tool.use("InvalidCity")
        assert result == "Could not find weather for InvalidCity."
        mock_get.assert_called_once()

    def test_use_no_api_key(self, weather_tool):
        """Test missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError):
                weather_tool.use("Bangalore")

    @patch.dict(os.environ, {"OPENWEATHERMAP_API_KEY": "test_api_key"})
    @patch('requests.get')
    def test_use_network_error(self, mock_get, weather_tool):
        """Test network error."""
        mock_get.side_effect = Exception("Network error")

        result = weather_tool.use("Bangalore")
        assert "Could not find weather" in result
        assert "Network error" in result
