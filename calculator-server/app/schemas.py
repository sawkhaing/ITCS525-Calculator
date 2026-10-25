from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class BaseExpression(BaseModel):
    expr: str


class ExpressionIn(BaseExpression):
    """The expression submitted by the client."""


class ExpressionOut(ExpressionIn):
    """A history entry extends the input with its result and timestamp."""

    result: Any
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
