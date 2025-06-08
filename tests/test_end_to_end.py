"""
End-to-end tests for Orchestratex workflows
"""

import pytest
from src.example import calculate

def test_end_to_end_workflow():
    """Simulate a workflow and assert the final result."""
    # Step 1: Add two numbers
    sum_result = calculate(2, 3, 'add')
    assert sum_result == 5

    # Step 2: Multiply the result
    final_result = calculate(sum_result, 2, 'multiply')
    assert final_result == 10

@pytest.mark.parametrize("input_a,input_b,operation,expected", [
    (1, 2, 'add', 3),
    (2, 3, 'multiply', 6),
    (0, 0, 'add', 0),
])
def test_end_to_end_various(input_a, input_b, operation, expected):
    """Test end-to-end workflow with various inputs."""
    result = calculate(input_a, input_b, operation)
    assert result == expected

def test_end_to_end_error_handling():
    """Test error handling in end-to-end workflow."""
    with pytest.raises(ValueError):
        calculate(2, 3, 'invalid_operation')
