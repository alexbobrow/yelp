import logging
from dataclasses import dataclass

from domain.models import Company, CompanySummary
from domain.repositories import ICompanyRepository

logger = logging.getLogger(__name__)


class GetCompanyByIdUseCase:
    def __init__(self, company_repo: ICompanyRepository):
        self.company_repo = company_repo

    async def execute(self, company_id: int) -> Company | None:
        return await self.company_repo.get_by_id(company_id)


@dataclass
class CompaniesListUseCaseRequest:
    building_id: int | None
    activity_id: int | None
    activity_children: bool
    name: str | None
    lat: float | None
    lng: float | None
    radius: int | None
    latx: float | None
    lngx: float | None
    laty: float | None
    lngy: float | None
    offset: int


@dataclass
class CompaniesListUseCaseResponse:
    items: list[CompanySummary]
    total: int


class CompaniesListUseCase:
    def __init__(self, company_repo: ICompanyRepository):
        self.company_repo = company_repo

    async def execute(self, request: CompaniesListUseCaseRequest) -> CompaniesListUseCaseResponse:
        companies, total = await self.company_repo.list_filtered(
            building_id=request.building_id,
            activity_id=request.activity_id,
            activity_children=request.activity_children,
            name=request.name,
            lat=request.lat,
            lng=request.lng,
            radius=request.radius,
            latx=request.latx,
            lngx=request.lngx,
            laty=request.laty,
            lngy=request.lngy,
            offset=request.offset,
        )
        return CompaniesListUseCaseResponse(items=companies, total=total)
