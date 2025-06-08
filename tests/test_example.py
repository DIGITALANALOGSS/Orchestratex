"""
Unit tests for the example module
"""

import pytest
from src.example import add, multiply, calculate

def test_add_positive_numbers():
    """Test that add() correctly sums two positive numbers."""
    assert add(2, 3) == 5

def test_add_negative_numbers():
    """Test that add() correctly sums two negative numbers."""
    assert add(-2, -3) == -5

@pytest.mark.parametrize("a,b,expected", [
    (0, 0, 0),
    (1, -1, 0),
    (-1, 1, 0),
])
def test_add_various(a, b, expected):
    """Test add() with multiple cases using parametrize."""
    assert add(a, b) == expected

def test_multiply():
    """Test that multiply() correctly multiplies numbers."""
    assert multiply(2, 3) == 6
    assert multiply(-2, 3) == -6
    assert multiply(-2, -3) == 6

def test_calculate_add():
    """Test calculate() with addition operation."""
    assert calculate(2, 3, 'add') == 5

def test_calculate_multiply():
    """Test calculate() with multiplication operation."""
    assert calculate(2, 3, 'multiply') == 6

def test_calculate_invalid_operation():
    """Test calculate() with invalid operation."""
    with pytest.raises(ValueError):
        calculate(2, 3, 'subtract')
