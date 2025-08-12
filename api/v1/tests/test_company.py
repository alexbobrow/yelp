from unittest.mock import AsyncMock
from urllib.parse import urlencode

import pytest
from httpx import AsyncClient
from starlette import status

from api.v1.schemas import CompanyResponse, CompanyListResponse, CompanySummaryResponse
from domain.tests.factories import CompanyFactory, CompanySummaryFactory
from usecases.company import CompaniesListUseCaseResponse, CompaniesListUseCaseRequest


@pytest.mark.asyncio
class TestGetCompanyById:
    async def test_unauthorized_no_token(self, guest_client: AsyncClient) -> None:
        request_response = await guest_client.get("/api/v1/companies/1/")
        assert request_response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unauthorized_wrong_token(self, guest_client: AsyncClient) -> None:
        headers = {"Authorization": "Token wrongtoken"}
        request_response = await guest_client.get("/api/v1/companies/1/", headers=headers)
        assert request_response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_found(self, get_company_by_id_mock: AsyncMock, client: AsyncClient) -> None:
        mock_company = CompanyFactory()
        get_company_by_id_mock.execute.return_value = mock_company
        request_response = await client.get("/api/v1/companies/1/")
        assert request_response.status_code == status.HTTP_200_OK
        data = request_response.json()
        response = CompanyResponse(**data)
        expected_response = CompanyResponse.model_validate(mock_company, from_attributes=True)
        assert response == expected_response
        get_company_by_id_mock.execute.assert_awaited_once_with(1)

    async def test_not_found(self, get_company_by_id_mock: AsyncMock, client: AsyncClient) -> None:
        get_company_by_id_mock.execute.return_value = None
        response = await client.get("/api/v1/companies/1/")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        get_company_by_id_mock.execute.assert_awaited_once_with(1)


@pytest.mark.asyncio
class TestCompaniesList:
    async def test_unauthorized_no_token(self, guest_client: AsyncClient) -> None:
        request_response = await guest_client.get("/api/v1/companies/")
        assert request_response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_unauthorized_wrong_token(self, guest_client: AsyncClient) -> None:
        headers = {"Authorization": "Token wrongtoken"}
        request_response = await guest_client.get("/api/v1/companies/", headers=headers)
        assert request_response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_all(self, companies_list_mock: AsyncMock, client: AsyncClient) -> None:
        size = 10
        total = 15
        companies = CompanySummaryFactory.build_batch(size=size)
        companies_list_mock.execute.return_value = CompaniesListUseCaseResponse(
            items=companies,
            total=total,
        )
        request_response = await client.get("/api/v1/companies/")
        assert request_response.status_code == status.HTTP_200_OK
        data = request_response.json()
        response = CompanyListResponse(**data)
        expected_response = CompanyListResponse(
            items=[CompanySummaryResponse.model_validate(c, from_attributes=True) for c in companies],
            total=total,
        )
        assert response == expected_response
        expected_request = CompaniesListUseCaseRequest(
            building_id=None,
            activity_id=None,
            activity_children=False,
            name=None,
            lat=None,
            lng=None,
            radius=None,
            latx=None,
            lngx=None,
            laty=None,
            lngy=None,
            offset=0,
        )
        companies_list_mock.execute.assert_awaited_once_with(expected_request)

    async def test_with_parameters(self, companies_list_mock: AsyncMock, client: AsyncClient) -> None:
        size = 2
        total = 15
        companies = CompanySummaryFactory.build_batch(size=size)
        companies_list_mock.execute.return_value = CompaniesListUseCaseResponse(
            items=companies,
            total=total,
        )
        params = dict(
            building_id=1,
            activity_id=2,
            activity_children="true",
            name="Name",
            lat=11.11,
            lng=22.22,
            radius=3,
            latx=44.44,
            lngx=55.55,
            laty=66.66,
            lngy=77.77,
            offset=8,
        )
        request_response = await client.get(f"/api/v1/companies/?{urlencode(params)}")
        assert request_response.status_code == status.HTTP_200_OK
        data = request_response.json()
        response = CompanyListResponse(**data)
        expected_response = CompanyListResponse(
            items=[CompanySummaryResponse.model_validate(c, from_attributes=True) for c in companies],
            total=total,
        )
        assert response == expected_response
        params["activity_children"] = True
        expected_request = CompaniesListUseCaseRequest(**params)  # type: ignore[arg-type]
        companies_list_mock.execute.assert_awaited_once_with(expected_request)
