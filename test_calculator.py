#test_calculator.py

import pytest
from calculator import expand_percent
from models import Expression, CalculatorLog

def test_add_percent():
    """Test addition where B% means 'B percent of A'."""
    assert expand_percent("5 + 10%") == "5 + ((10/100)*5)"

def test_subtract_percent():
    """Test subtraction where B% means 'B percent of A'."""
    assert expand_percent("20 - 30%") == "20 - ((30/100)*20)"

def test_multiply_percent():
    """Test multiplication where B% means 'B divided by 100'."""
    assert expand_percent("15 * 25%") == "15 * (25/100)"

def test_divide_percent():
    """Test division where B% means 'B divided by 100'."""
    assert expand_percent("40 / 50%") == "40 / (50/100)"

def test_multiple_operations():
    """Test expressions with multiple A op B% operations."""
    assert expand_percent("3 * 4% + 2 / 1%") == "3 * (4/100) + 2 / (1/100)"

def test_standalone_100_percent():
    """Test standalone percentage (100%)."""
    assert expand_percent("100%") == "(100/100)"

def test_two_standalone_percents():
    """Test expression with two standalone percentages."""
    assert expand_percent("10% + 20%") == "(10/100) + (20/100)"

def test_expression_model_expand_percent():
    """Test Expression model's expand_percent method."""
    expr_obj = Expression(expr="100 - 6%")
    assert expr_obj.expand_percent() == "100 - ((6/100)*100)"

def test_calculator_log_model():
    """Test CalculatorLog model instantiation and default timestamp."""
    log = CalculatorLog(expr="2 + 2", result=4)
    assert log.expr == "2 + 2"
    assert log.result == 4
    assert log.timestamp is not None

