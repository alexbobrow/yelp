from abc import ABC, abstractmethod

from domain.models import Company, CompanySummary


class ICompanyRepository(ABC):
    @abstractmethod
    async def get_by_id(self, company_id: int) -> Company | None: ...

    @abstractmethod
    async def list_filtered(
        self,
        building_id: int | None = None,
        activity_id: int | None = None,
        activity_children: bool = False,
        name: str | None = None,
        lat: float | None = None,
        lng: float | None = None,
        radius: int | None = None,
        latx: float | None = None,
        lngx: float | None = None,
        laty: float | None = None,
        lngy: float | None = None,
        offset: int = 0,
    ) -> tuple[list[CompanySummary], int]: ...
