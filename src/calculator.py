"""
Calculator module with basic arithmetic operations

This module provides functions for performing basic arithmetic operations with
proper error handling and input validation.
"""

def add(a: float, b: float) -> float:
    """Add two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Sum of a and b

    Raises:
        TypeError: If inputs are not numbers
        OverflowError: If result exceeds maximum float value
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers")
    
    result = a + b
    if not (float('-inf') < result < float('inf')):
        raise OverflowError("Result exceeds maximum float value")
    return result

def subtract(a: float, b: float) -> float:
    """Subtract b from a.

    Args:
        a: First number
        b: Second number

    Returns:
        Result of a - b

    Raises:
        TypeError: If inputs are not numbers
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers")
    return a - b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers.

    Args:
        a: First number
        b: Second number

    Returns:
        Product of a and b

    Raises:
        TypeError: If inputs are not numbers
        OverflowError: If result exceeds maximum float value
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers")
    
    result = a * b
    if not (float('-inf') < result < float('inf')):
        raise OverflowError("Result exceeds maximum float value")
    return result

def divide(a: float, b: float) -> float:
    """Divide a by b.

    Args:
        a: Numerator
        b: Denominator

    Returns:
        Result of a / b

    Raises:
        TypeError: If inputs are not numbers
        ZeroDivisionError: If b is zero
        OverflowError: If result exceeds maximum float value
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Inputs must be numbers")
    
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    
    result = a / b
    if not (float('-inf') < result < float('inf')):
        raise OverflowError("Result exceeds maximum float value")
    return result
