import pytest
from fastapi import HTTPException

from app import dependencies
from app.dependencies import expand_percent
from app.schemas import ExpressionIn

def test_add_percent():
    """Test addition where B% means 'B percent of A'."""
    e = ExpressionIn(expr="5 + 10%")
    assert expand_percent(e) == "5 + ((10/100)*5)"

def test_subtract_percent():
    """Test subtraction where B% means 'B percent of A'."""
    e = ExpressionIn(expr="20 - 30%")
    assert expand_percent(e) == "20 - ((30/100)*20)"

def test_multiply_percent():
    """Test multiplication where B% means 'B divided by 100'."""
    e = ExpressionIn(expr="15 * 25%")
    assert expand_percent(e) == "15 * (25/100)"

def test_divide_percent():
    """Test division where B% means 'B divided by 100'."""
    e = ExpressionIn(expr="40 / 50%")
    assert expand_percent(e) == "40 / (50/100)"

def test_multiple_operations():
    """Test expressions with multiple A op B% operations."""
    e = ExpressionIn(expr="3 * 4% + 2 / 1%")
    assert expand_percent(e) == "3 * (4/100) + 2 / (1/100)"

def test_standalone_100_percent():
    """Test standalone percentage (100%)."""
    e = ExpressionIn(expr="100%")
    assert expand_percent(e) == "(100/100)"

def test_two_standalone_percents():
    """Test expression with two standalone percentages."""
    e = ExpressionIn(expr="10% + 20%")
    assert expand_percent(e) == "(10/100) + (20/100)"


def test_normalize_symbols_before_expanding():
    assert expand_percent(ExpressionIn(expr="100 − 6%")) == "100 - ((6/100)*100)"
    assert expand_percent(ExpressionIn(expr="40 ÷ 50%")) == "40 / (50/100)"


def test_expansion_failure_is_http_error(monkeypatch):
    class BrokenPattern:
        def search(self, expression):
            raise ValueError("Expansion failed")

    monkeypatch.setattr(dependencies, "_percent_pair", BrokenPattern())
    with pytest.raises(HTTPException) as exc:
        expand_percent(ExpressionIn(expr="5 + 10%"))
    assert exc.value.status_code == 400

