from dataclasses import dataclass


@dataclass
class Phone:
    id: int
    number: str


@dataclass
class Building:
    id: int
    address: str
    latitude: float
    longitude: float


@dataclass
class Activity:
    id: int
    name: str
    parent_id: int | None = None


@dataclass
class Company:
    id: int
    name: str
    legal_form: str
    building: Building
    phones: list[Phone]
    activities: list[Activity]


@dataclass
class CompanySummary:
    id: int
    name: str
    legal_form: str
