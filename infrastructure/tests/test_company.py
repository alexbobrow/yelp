import pytest
from geoalchemy2.shape import to_shape
from sqlalchemy.ext.asyncio import AsyncSession

from config.containers import Container
from domain.models import Company, Building, Phone, Activity, CompanySummary
from infrastructure.models.models import CompanyOrm, ActivityOrm
from infrastructure.tests.factories import (
    BuildingOrmFactory,
    CompanyOrmFactory,
    ActivityOrmFactory,
    PhoneOrmFactory,
)


class TestCompanyRepository:
    @pytest.mark.asyncio
    async def test_get_by_id(self, db: AsyncSession, container: Container) -> None:
        building_orm = BuildingOrmFactory()
        activity_orm_1, activity_orm_2 = ActivityOrmFactory(), ActivityOrmFactory()
        db.add_all([building_orm, activity_orm_1, activity_orm_2])
        await db.flush()

        company_orm = CompanyOrmFactory(
            building=building_orm,
            activities=[activity_orm_1, activity_orm_2],
        )
        db.add(company_orm)
        await db.flush()

        phone_orm_1, phone_orm_2 = PhoneOrmFactory.build_batch(size=2, company=company_orm)
        db.add_all([phone_orm_1, phone_orm_2])
        await db.commit()

        point = to_shape(building_orm.coordinates)
        repo = container.company_repo()
        res = await repo.get_by_id(company_orm.id)

        expected_res = Company(
            id=company_orm.id,
            name=company_orm.name,
            legal_form=company_orm.legal_form,
            building=Building(
                id=building_orm.id,
                address=building_orm.address,
                latitude=point.x,
                longitude=point.y,
            ),
            phones=[
                Phone(id=phone_orm_1.id, number=phone_orm_1.number),
                Phone(id=phone_orm_2.id, number=phone_orm_2.number),
            ],
            activities=[
                Activity(id=activity_orm_1.id, name=activity_orm_1.name, parent_id=None),
                Activity(id=activity_orm_2.id, name=activity_orm_2.name, parent_id=None),
            ],
        )
        assert res == expected_res

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, container: Container) -> None:
        repo = container.company_repo()
        res = await repo.get_by_id(-1)
        assert res is None

    @pytest.mark.asyncio
    async def test_list_filtered_all(self, db: AsyncSession, container: Container) -> None:
        building_orm = BuildingOrmFactory()
        db.add(building_orm)
        await db.flush()
        companies_count = 11
        companies_orm = CompanyOrmFactory.build_batch(size=companies_count, building=building_orm)
        db.add_all(companies_orm)
        await db.flush()

        repo = container.company_repo()
        settings = container.settings()
        res = await repo.list_filtered()
        assert all([isinstance(c, CompanySummary) for c in res[0]]) is True
        assert len(res[0]) == settings.company_items_per_page
        assert res[1] == companies_count

        offset = 10
        res = await repo.list_filtered(offset=offset)
        assert all([isinstance(c, CompanySummary) for c in res[0]]) is True
        assert len(res[0]) == res[1] - offset
        assert res[1] == companies_count

    @pytest.mark.asyncio
    async def test_list_filtered_by_params(
        self,
        container: Container,
        activities_tree_orm: tuple[ActivityOrm, ...],
        companies_search_setup: tuple[CompanyOrm, ...],
    ) -> None:
        food, auto, cars, spare, engine = activities_tree_orm
        food_company, auto_company, cars_company, spare_company, engine_company = companies_search_setup

        repo = container.company_repo()

        # search by name
        res = await repo.list_filtered(name="моск")
        assert len(res[0]) == 1
        assert res[0][0].id == food_company.id
        assert res[1] == 1

        # search by building
        res = await repo.list_filtered(building_id=engine_company.building_id)
        assert len(res[0]) == 1
        assert res[0][0].id == engine_company.id
        assert res[1] == 1

        # search by particular activity
        res = await repo.list_filtered(activity_id=cars.id)
        assert len(res[0]) == 1
        assert res[0][0].id == cars_company.id
        assert res[1] == 1

        # search by activity with descendants activities of 3 level deep
        # should not give engine_company as it is level 4
        res = await repo.list_filtered(activity_id=auto.id, activity_children=True)
        assert len(res[0]) == 3
        assert res[1] == 3
        res_ids = {c.id for c in res[0]}
        expected_ids = {auto_company.id, cars_company.id, spare_company.id}
        assert res_ids == expected_ids

        # search by geo point and radius
        res = await repo.list_filtered(lng=37.6173, lat=55.7558, radius=500)  # exact point
        assert len(res[0]) == 1
        assert res[0][0].id == food_company.id

        res = await repo.list_filtered(lng=37.9269, lat=55.6806, radius=500)  # Lubertsi
        assert len(res[0]) == 0

        res = await repo.list_filtered(lng=37.9269, lat=55.6806, radius=22000)  # Lubertsi
        assert len(res[0]) == 1
        assert res[0][0].id == food_company.id

        # search by geo square coordinates
        res = await repo.list_filtered(lngx=37.4275, latx=55.7571, lngy=37.7994, laty=55.6241)  # Moscow square
        assert len(res[0]) == 1
        assert res[0][0].id == food_company.id

        res = await repo.list_filtered(lngx=40.4275, latx=50.7571, lngy=40.7994, laty=50.6241)  # Wrong square
        assert len(res[0]) == 0
