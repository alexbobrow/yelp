from typing import Generator
from unittest.mock import create_autospec, AsyncMock

import pytest

from config.containers import Container
from domain.repositories import ICompanyRepository


@pytest.fixture
def company_repo_mock(container: Container) -> Generator[AsyncMock, None, None]:
    mock = create_autospec(ICompanyRepository)
    container.company_repo.override(mock)
    yield mock
