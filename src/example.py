"""
Example module for Orchestratex

This module contains example functions to demonstrate testing.
"""

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

def calculate(a: int, b: int, operation: str) -> int:
    """Perform a calculation based on the operation.

    Args:
        a: First number
        b: Second number
        operation: Operation to perform ('add' or 'multiply')

    Returns:
        Result of the calculation

    Raises:
        ValueError: If operation is not supported
    """
    if operation == 'add':
        return add(a, b)
    elif operation == 'multiply':
        return multiply(a, b)
    else:
        raise ValueError(f"Unsupported operation: {operation}")
