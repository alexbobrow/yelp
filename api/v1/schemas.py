from pydantic import BaseModel


class PhoneResponse(BaseModel):
    id: int
    number: str


class BuildingResponse(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float


class ActivityResponse(BaseModel):
    id: int
    name: str
    parent_id: int | None = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    legal_form: str
    building: BuildingResponse
    phones: list[PhoneResponse]
    activities: list[ActivityResponse]


class CompanySummaryResponse(BaseModel):
    id: int
    name: str
    legal_form: str


class CompanyListResponse(BaseModel):
    items: list[CompanySummaryResponse]
    total: int
