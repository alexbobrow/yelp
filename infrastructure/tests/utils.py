from typing import TypeVar

from geoalchemy2 import WKTElement
from sqlalchemy.ext.asyncio import AsyncSession

from config.const import COORDS_SYSTEM_2D
from infrastructure.models.models import ActivityOrm, CompanyOrm
from infrastructure.tests.const import COORDS_MOSCOW, COORDS_REGION
from infrastructure.tests.factories import BuildingOrmFactory, CompanyOrmFactory

T = TypeVar("T")


async def create_async(db: AsyncSession, model: T) -> T:
    db.add(model)
    await db.flush()
    return model


async def create_demo_activities(db: AsyncSession) -> tuple[ActivityOrm, ...]:
    """
    Еда
    Автомобили
        Легковые
            Запчасти
                Двигатель
    """
    food = await create_async(db=db, model=ActivityOrm(name="Еда"))
    auto = await create_async(db=db, model=ActivityOrm(name="Автомобили"))
    cars = await create_async(db=db, model=ActivityOrm(name="Легковые", parent_id=auto.id))
    spare = await create_async(db=db, model=ActivityOrm(name="Запчасти", parent_id=cars.id))
    engine = await create_async(db=db, model=ActivityOrm(name="Двигатель", parent_id=spare.id))
    return food, auto, cars, spare, engine


async def create_demo_companies(
    db: AsyncSession,
    activities: tuple[ActivityOrm, ...],
) -> tuple[CompanyOrm, ...]:
    food, auto, cars, spare, engine = activities
    point_moscow = WKTElement(f"POINT({COORDS_MOSCOW[0]} {COORDS_MOSCOW[1]})", srid=COORDS_SYSTEM_2D)
    point_region = WKTElement(f"POINT({COORDS_REGION[0]} {COORDS_REGION[1]})", srid=COORDS_SYSTEM_2D)

    food_building = await create_async(db=db, model=BuildingOrmFactory(coordinates=point_moscow))
    food_company = await create_async(
        db=db,
        model=CompanyOrmFactory(
            name="Московская еда",
            building_id=food_building.id,
            activities=[food],
        ),
    )

    auto_building = await create_async(db=db, model=BuildingOrmFactory(coordinates=point_region))
    auto_company = await create_async(
        db=db,
        model=CompanyOrmFactory(
            name="Компания автомобилей",
            building_id=auto_building.id,
            activities=[auto],
        ),
    )

    cars_building = await create_async(db=db, model=BuildingOrmFactory(coordinates=point_region))
    cars_company = await create_async(
        db=db,
        model=CompanyOrmFactory(name="Компания легковых", building_id=cars_building.id, activities=[cars]),
    )

    spare_building = await create_async(db=db, model=BuildingOrmFactory(coordinates=point_region))
    spare_company = await create_async(
        db=db,
        model=CompanyOrmFactory(
            name="Компания запчастей",
            building_id=spare_building.id,
            activities=[spare],
        ),
    )

    engine_building = await create_async(db=db, model=BuildingOrmFactory(coordinates=point_region))
    engine_company = await create_async(
        db=db,
        model=CompanyOrmFactory(
            name="Компания двигателей",
            building_id=engine_building.id,
            activities=[engine],
        ),
    )

    return food_company, auto_company, cars_company, spare_company, engine_company
