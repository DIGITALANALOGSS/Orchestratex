"""
Tests for ModelManager
"""

import pytest
import asyncio
from orchestratex.core.models import ModelManager, AWSBedrockModel, AnthropicClaudeModel

class TestModelManager:
    """Test cases for ModelManager."""

    @pytest.fixture
    def model_manager(self):
        """Model manager fixture."""
        return ModelManager()

    @pytest.mark.asyncio
    async def test_aws_bedrock_model(self, model_manager):
        """Test AWS Bedrock model integration."""
        prompt = "Hello AWS"
        result = await model_manager.generate("aws_bedrock", prompt)
        assert result.startswith("AWS Bedrock response to:")
        assert prompt in result

    @pytest.mark.asyncio
    async def test_anthropic_claude_model(self, model_manager):
        """Test Anthropic Claude model integration."""
        prompt = "Hello Claude"
        result = await model_manager.generate("anthropic_claude", prompt)
        assert result.startswith("Anthropic Claude 3-opus response to:")
        assert prompt in result

    @pytest.mark.asyncio
    async def test_model_not_found(self, model_manager):
        """Test handling of non-existent model."""
        with pytest.raises(ValueError):
            await model_manager.generate("nonexistent_model", "test")

    @pytest.mark.asyncio
    async def test_concurrent_generation(self, model_manager):
        """Test concurrent model generation."""
        prompts = [
            "Hello AWS",
            "Hello Claude",
            "Test AWS",
            "Test Claude"
        ]

        # Run concurrent generation
        tasks = [
            model_manager.generate("aws_bedrock", prompts[0]),
            model_manager.generate("anthropic_claude", prompts[1]),
            model_manager.generate("aws_bedrock", prompts[2]),
            model_manager.generate("anthropic_claude", prompts[3])
        ]
        results = await asyncio.gather(*tasks)

        assert len(results) == 4
        for i, result in enumerate(results):
            if i % 2 == 0:  # AWS Bedrock responses
                assert result.startswith("AWS Bedrock response to:")
            else:  # Claude responses
                assert result.startswith("Anthropic Claude 3-opus response to:")

    @pytest.mark.asyncio
    async def test_custom_model_versions(self, model_manager):
        """Test custom model versions."""
        # Test custom AWS Bedrock model
        custom_aws = AWSBedrockModel(model_id="custom-model")
        result = await custom_aws.generate("Test custom AWS")
        assert result.startswith("AWS Bedrock response to:")

        # Test custom Claude version
        custom_claude = AnthropicClaudeModel(version="custom-version")
        result = await custom_claude.generate("Test custom Claude")
        assert result.startswith("Anthropic Claude custom-version response to:")

    @pytest.mark.asyncio
    async def test_model_registration(self, model_manager):
        """Test model registration."""
        # Register new models
        model_manager.models["custom_aws"] = AWSBedrockModel(model_id="custom-model")
        model_manager.models["custom_claude"] = AnthropicClaudeModel(version="custom-version")

        # Test new models
        aws_result = await model_manager.generate("custom_aws", "Test custom AWS")
        claude_result = await model_manager.generate("custom_claude", "Test custom Claude")

        assert aws_result.startswith("AWS Bedrock response to:")
        assert claude_result.startswith("Anthropic Claude custom-version response to:")
