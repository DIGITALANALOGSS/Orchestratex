"""
Tests for the RAGMaestro
"""

import pytest
from orchestratex.agents.rag_maestro import RAGMaestro
from unittest.mock import MagicMock

class TestRAGMaestro:
    """Test cases for the RAGMaestro."""

    @pytest.fixture
    def mock_model(self):
        """Mock model fixture."""
        model = MagicMock()
        model.retrieve = MagicMock(return_value="Knowledge snippet")
        return model

    @pytest.fixture
    def rag_maestro(self, mock_model):
        """RAG Maestro fixture."""
        return RAGMaestro(
            name="RAG Maestro",
            description="Retrieves and synthesizes knowledge",
            tools=[],
            model=mock_model
        )

    def test_process_input(self, rag_maestro, mock_model):
        """Test processing input."""
        result = rag_maestro.process_input("What is AI?")
        assert result == "Knowledge snippet"
        mock_model.retrieve.assert_called_once_with("What is AI?")

    def test_memory_tracking(self, rag_maestro, mock_model):
        """Test memory tracking."""
        mock_model.retrieve.return_value = "Knowledge snippet"
        rag_maestro.process_input("What is AI?")
        assert len(rag_maestro.memory) > 0
        assert "Context: Knowledge snippet" in rag_maestro.memory[0]

    def test_empty_input(self, rag_maestro):
        """Test handling empty input."""
        mock_model = rag_maestro.model
        mock_model.retrieve.return_value = ""
        result = rag_maestro.process_input("")
        assert result == ""
        mock_model.retrieve.assert_called_once_with("")

    def test_large_input(self, rag_maestro):
        """Test handling large input."""
        large_input = " " * 1000000
        mock_model = rag_maestro.model
        mock_model.retrieve.return_value = "Snippet"
        result = rag_maestro.process_input(large_input)
        assert result == "Snippet"
        mock_model.retrieve.assert_called_once_with(large_input)

    def test_error_handling(self, rag_maestro):
        """Test error handling."""
        mock_model = rag_maestro.model
        mock_model.retrieve.side_effect = Exception("Retrieval error")
        with pytest.raises(Exception):
            rag_maestro.process_input("Test")
        assert len(rag_maestro.memory) == 0
