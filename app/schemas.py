from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field

class BaseExpression(BaseModel):
    expr: str

class ExpressionIn(BaseExpression):
    pass

class ExpressionOut(BaseExpression):
    result: Union[float, int, str]

# Alias for compatibility with old imports in tests
Expression = ExpressionIn

class CalculatorLog(ExpressionOut):
    timestamp: datetime = Field(default_factory=datetime.now)
