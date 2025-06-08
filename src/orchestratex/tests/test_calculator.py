"""
Comprehensive test suite for the calculator module

This test suite covers all aspects of the calculator functionality including:
- Basic operations
- Edge cases
- Error handling
- Performance
- Security
"""

import pytest
import time
from src.calculator import add, subtract, multiply, divide

@pytest.fixture(scope="module")
def sample_data():
    """Provide reusable test data for the module."""
    return {
        "positives": (10, 5),
        "negatives": (-10, -5),
        "mixed": (10, -5),
        "zero": (0, 10),
        "large": (1e100, 1e100),
        "small": (1e-100, 1e-100)
    }

# Addition Tests
class TestAddition:
    """Robust tests for add() with edge and error cases."""

    @pytest.mark.parametrize("a,b,expected", [
        (1, 2, 3),
        (-1, -1, -2),
        (0, 0, 0),
        (1e10, 1e10, 2e10),
        (1e-10, 1e-10, 2e-10)
    ])
    def test_add_various(self, a, b, expected):
        """Test add() with a variety of numbers."""
        assert add(a, b) == expected

    def test_add_type_error(self, sample_data):
        """Test add() raises TypeError on invalid input."""
        with pytest.raises(TypeError):
            add("a", 1)
        with pytest.raises(TypeError):
            add(sample_data["positives"], 1)  # Test with tuple

    def test_add_overflow(self):
        """Test add() with very large numbers."""
        with pytest.raises(OverflowError):
            add(1e308, 1e308)

# Subtraction Tests
class TestSubtraction:
    """Advanced subtraction tests including boundary and negative cases."""

    @pytest.mark.parametrize("a,b,expected", [
        (5, 3, 2),
        (3, 5, -2),
        (0, 0, 0),
        (-5, -3, -2),
        (1e10, 1e10, 0)
    ])
    def test_subtract_various(self, a, b, expected):
        """Test subtract() with various cases."""
        assert subtract(a, b) == expected

    def test_subtract_type_error(self, sample_data):
        """Test subtract() with invalid types."""
        with pytest.raises(TypeError):
            subtract("a", 1)
        with pytest.raises(TypeError):
            subtract(sample_data["positives"], 1)

# Multiplication Tests
class TestMultiplication:
    """Multiplication tests with zero, negatives, and large numbers."""

    @pytest.mark.parametrize("a,b,expected", [
        (2, 3, 6),
        (0, 100, 0),
        (-2, 3, -6),
        (1e5, 1e5, 1e10),
        (1e-5, 1e-5, 1e-10)
    ])
    def test_multiply_various(self, a, b, expected):
        """Test multiply() with various cases."""
        assert multiply(a, b) == expected

    def test_multiply_type_error(self, sample_data):
        """Test multiply() with invalid types."""
        with pytest.raises(TypeError):
            multiply("a", 1)
        with pytest.raises(TypeError):
            multiply(sample_data["positives"], 1)

    def test_multiply_overflow(self):
        """Test multiply() with very large numbers."""
        with pytest.raises(OverflowError):
            multiply(1e308, 1e308)

# Division Tests
class TestDivision:
    """Division tests with error handling and edge cases."""

    @pytest.mark.parametrize("a,b,expected", [
        (10, 2, 5),
        (-10, 2, -5),
        (0, 1, 0),
        (1e10, 1e10, 1)
    ])
    def test_divide_various(self, a, b, expected):
        """Test divide() with various cases."""
        assert divide(a, b) == expected

    def test_divide_by_zero(self):
        """Test division by zero."""
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

    def test_divide_type_error(self, sample_data):
        """Test divide() with invalid types."""
        with pytest.raises(TypeError):
            divide("10", 2)
        with pytest.raises(TypeError):
            divide(sample_data["positives"], 1)

    def test_divide_overflow(self):
        """Test divide() with very large numbers."""
        with pytest.raises(OverflowError):
            divide(1e308, 1e-308)

# Integration/E2E Tests
def test_end_to_end_calculation(sample_data):
    """Simulate a complete calculation workflow."""
    a, b = sample_data["positives"]
    result = add(a, b)
    result = multiply(result, 2)
    result = subtract(result, 5)
    assert result == ((a + b) * 2) - 5

# Performance Tests
def test_performance_addition():
    """Test add() performance with large input."""
    start = time.time()
    for _ in range(1000000):
        add(123456, 654321)
    duration = time.time() - start
    assert duration < 2  # seconds

def test_performance_division():
    """Test divide() performance with large input."""
    start = time.time()
    for _ in range(1000000):
        divide(123456, 654321)
    duration = time.time() - start
    assert duration < 2  # seconds

# Security Tests
def test_no_code_injection():
    """Ensure calculator functions do not execute code from input."""
    malicious_input = "__import__('os').system('rm -rf /')"
    with pytest.raises(TypeError):
        add(malicious_input, 1)
    with pytest.raises(TypeError):
        subtract(malicious_input, 1)
    with pytest.raises(TypeError):
        multiply(malicious_input, 1)
    with pytest.raises(TypeError):
        divide(malicious_input, 1)

def test_no_eval_execution():
    """Ensure calculator functions do not execute eval() or exec()."""
    with pytest.raises(TypeError):
        add("eval('1+1')", 1)
    with pytest.raises(TypeError):
        subtract("exec('print("hello")')", 1)

# Edge Case Tests
def test_edge_cases(sample_data):
    """Test calculator with edge cases."""
    # Test with very small numbers
    small_a, small_b = sample_data["small"]
    assert add(small_a, small_b) == 2 * small_a
    assert subtract(small_a, small_b) == 0
    assert multiply(small_a, small_b) == small_a * small_b
    assert divide(small_a, small_b) == 1

    # Test with very large numbers
    large_a, large_b = sample_data["large"]
    assert add(large_a, large_b) == 2 * large_a
    assert subtract(large_a, large_b) == 0
    assert multiply(large_a, large_b) == large_a * large_b
    assert divide(large_a, large_b) == 1
