import pytest

from app.dependencies import get_history
from app.main import app


@pytest.fixture(autouse=True)
def reset_history():
    get_history().clear()
    yield
    app.dependency_overrides.clear()
    get_history().clear()
