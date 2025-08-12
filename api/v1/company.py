import dataclasses

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import token_auth
from api.v1.schemas import CompanyResponse, CompanyListResponse, CompanySummaryResponse
from config.containers import Container
from usecases.company import (
    CompaniesListUseCaseRequest,
    GetCompanyByIdUseCase,
    CompaniesListUseCase,
)


company_router = APIRouter(prefix="/v1/companies")

companies_list_description = """
Returns a list of companies, optionally filtered by GET parameters. Filtering parameters may be combined. The result is
limited to 10 items starting from the offset.

Retrieve all companies:

`/api/v1/companies/`

Next GET parameters are available to filter companies:

## building_id
Filters companies by a particular building ID.

 `/api/v1/companies/?building_id=1`

## activity_id
Filters companies by a particular activity ID.

`/api/v1/companies/?activity_id=1`

## activity_children
Used in pair with activity_id. If true takes into account 3 levels of activity depth. Defaults to false.

`/api/v1/companies/?activity_id=1&activity_children=true`

## name
Search companies that contains provided string. Case insensitive.

`/api/v1/companies/?name=test`

## lng, lat, radius
Used together. Defines the longitude/latitude coordinate of the point and radius in meters within which to search for
companies.

`/api/v1/companies/?lng=37.6173&lat=55.7558&radius=500`

## lngx, latx, lngy, laty
Used together. Defines the longitude/latitude coordinates of the rectangle within which to search for companies.

`/api/v1/companies/?lngx=37.4275&latx=55.7571&lngy=37.7994&laty=55.6241`

## offset
Defines the offset for companies for pagination. Default to 0.

`/api/v1/companies/?offset=10`
"""


@company_router.get(
    "/{company_id}/",
    response_model=CompanyResponse,
    summary="Retrieve a company info by ID",
    description="Returns detailed information about a company by its ID",
    dependencies=[Depends(token_auth)],
)
@inject
async def get_company_by_id(
    company_id: int,
    use_case: GetCompanyByIdUseCase = Depends(Provide[Container.get_company_by_id_uc]),
) -> CompanyResponse:
    company = await use_case.execute(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.model_validate(dataclasses.asdict(company))


@company_router.get(
    "/",
    response_model=CompanyListResponse,
    summary="Retrieve companies",
    description=companies_list_description,
    dependencies=[Depends(token_auth)],
)
@inject
async def list_companies(
    building_id: int | None = Query(None),
    activity_id: int | None = Query(None),
    activity_children: bool = Query(False),
    name: str | None = Query(None),
    lat: float | None = Query(None),
    lng: float | None = Query(None),
    radius: int | None = Query(None),
    latx: float | None = Query(None),
    lngx: float | None = Query(None),
    laty: float | None = Query(None),
    lngy: float | None = Query(None),
    offset: int = Query(0),
    use_case: CompaniesListUseCase = Depends(Provide[Container.companies_list_uc]),
) -> CompanyListResponse:
    request = CompaniesListUseCaseRequest(
        building_id=building_id,
        activity_id=activity_id,
        activity_children=activity_children,
        name=name,
        lat=lat,
        lng=lng,
        radius=radius,
        latx=latx,
        lngx=lngx,
        laty=laty,
        lngy=lngy,
        offset=offset,
    )
    response = await use_case.execute(request)
    items = [CompanySummaryResponse.model_validate(x, from_attributes=True) for x in response.items]
    return CompanyListResponse(items=items, total=response.total)
