from typing import Generator
from unittest.mock import AsyncMock

import pytest

from config.containers import Container


@pytest.fixture
def get_company_by_id_mock(container: Container) -> Generator[AsyncMock, None, None]:
    mock = AsyncMock()
    container.get_company_by_id_uc.override(mock)
    yield mock


@pytest.fixture
def companies_list_mock(container: Container) -> Generator[AsyncMock, None, None]:
    mock = AsyncMock()
    container.companies_list_uc.override(mock)
    yield mock
