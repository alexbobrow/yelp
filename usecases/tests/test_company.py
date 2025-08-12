import dataclasses
from unittest.mock import AsyncMock

import pytest

from config.containers import Container
from domain.tests.factories import CompanyFactory, CompanySummaryFactory
from usecases.company import CompaniesListUseCaseResponse
from usecases.tests.factories import CompaniesListUseCaseRequestFactory


@pytest.mark.asyncio
class TestGetCompanyByIdUseCase:
    async def test_company_found(self, container: Container, company_repo_mock: AsyncMock) -> None:
        uc = container.get_company_by_id_uc()
        id_arg = 1
        mock_company = CompanyFactory()
        company_repo_mock.get_by_id.return_value = mock_company
        result = await uc.execute(id_arg)
        assert result == mock_company
        company_repo_mock.get_by_id.assert_awaited_once_with(id_arg)

    async def test_company_not_found(self, container: Container, company_repo_mock: AsyncMock) -> None:
        uc = container.get_company_by_id_uc()
        id_arg = 1
        company_repo_mock.get_by_id.return_value = None
        result = await uc.execute(id_arg)
        assert result is None
        company_repo_mock.get_by_id.assert_awaited_once_with(id_arg)

    async def test_companies_list(self, container: Container, company_repo_mock: AsyncMock) -> None:
        size = 10
        total = 15
        uc = container.companies_list_uc()
        companies = CompanySummaryFactory.build_batch(size=size)
        company_repo_mock.list_filtered.return_value = companies, total
        request = CompaniesListUseCaseRequestFactory()
        result = await uc.execute(request)
        expected_result = CompaniesListUseCaseResponse(
            items=companies,
            total=total,
        )
        assert result == expected_result
        expected_args = dataclasses.asdict(request)
        company_repo_mock.list_filtered.assert_awaited_once_with(**expected_args)
