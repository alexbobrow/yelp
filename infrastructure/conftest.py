from typing import TypeVar

import pytest_asyncio
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.models.models import BuildingOrm, CompanyOrm, ActivityOrm
from infrastructure.tests.factories import (
    BuildingOrmFactory,
    CompanyOrmFactory,
)
from infrastructure.tests.utils import (
    create_async,
    create_demo_activities,
    create_demo_companies,
)

T = TypeVar("T")


fake = Faker()


@pytest_asyncio.fixture
async def building_orm(db: AsyncSession) -> BuildingOrm:
    return await create_async(db=db, model=BuildingOrmFactory())


@pytest_asyncio.fixture
async def company_orm(db: AsyncSession, building_orm: BuildingOrm) -> CompanyOrm:
    return await create_async(db=db, model=CompanyOrmFactory(building_id=building_orm.id))


@pytest_asyncio.fixture
async def activities_tree_orm(db: AsyncSession) -> tuple[ActivityOrm, ...]:
    return await create_demo_activities(db=db)


@pytest_asyncio.fixture
async def companies_search_setup(
    db: AsyncSession, activities_tree_orm: tuple[ActivityOrm, ...]
) -> tuple[CompanyOrm, ...]:
    return await create_demo_companies(
        db=db,
        activities=activities_tree_orm,
    )
