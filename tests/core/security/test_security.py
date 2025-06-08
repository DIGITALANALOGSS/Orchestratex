"""
Tests for SecurityGuard
"""

import pytest
from orchestratex.core.security import SecurityGuard
from unittest.mock import AsyncMock

class TestSecurityGuard:
    """Test cases for SecurityGuard."""

    @pytest.fixture
    def security_guard(self):
        """Security guard fixture."""
        return SecurityGuard()

    @pytest.mark.asyncio
    async def test_sql_injection_detection(self, security_guard):
        """Test SQL injection detection."""
        test_cases = [
            "DROP TABLE users;",
            "DELETE FROM users WHERE id = 1;",
            "TRUNCATE TABLE users;"
        ]
        
        for case in test_cases:
            with pytest.raises(SecurityError, match="SQL Injection"):
                await security_guard.sanitize_input({"query": case})

    @pytest.mark.asyncio
    async def test_xss_detection(self, security_guard):
        """Test XSS detection."""
        test_cases = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(1)'>",
            "javascript:alert('XSS')"
        ]
        
        for case in test_cases:
            with pytest.raises(SecurityError, match="XSS Attack"):
                await security_guard.sanitize_input({"content": case})

    @pytest.mark.asyncio
    async def test_command_injection_detection(self, security_guard):
        """Test command injection detection."""
        test_cases = [
            "|ls -la",
            "&& echo hello",
            "; rm -rf /"
        ]
        
        for case in test_cases:
            with pytest.raises(SecurityError, match="Command Injection"):
                await security_guard.sanitize_input({"command": case})

    @pytest.mark.asyncio
    async def test_valid_input(self, security_guard):
        """Test valid input processing."""
        valid_input = {
            "name": "John Doe",
            "age": "30",
            "city": "New York"
        }
        
        sanitized = await security_guard.sanitize_input(valid_input)
        assert sanitized == valid_input

    @pytest.mark.asyncio
    async def test_nested_input(self, security_guard):
        """Test sanitization of nested input."""
        nested_input = {
            "user": {
                "name": "John",
                "bio": "Developer"
            },
            "settings": {
                "theme": "dark",
                "notifications": True
            }
        }
        
        sanitized = await security_guard.sanitize_input(nested_input)
        assert sanitized == nested_input
