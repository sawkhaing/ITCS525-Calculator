from datetime import datetime
from typing import Union
from pydantic import BaseModel, Field

from calculator import expand_percent as _expand_percent


class Expression(BaseModel):
    expr: str

    def expand_percent(self) -> str:
        """Return the expression string after expanding percentage symbols."""
        return _expand_percent(self.expr)


class CalculatorLog(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    expr: str
    result: Union[float, int, str]
