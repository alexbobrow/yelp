from operator import and_, attrgetter

from geoalchemy2.functions import ST_DWithin
from geoalchemy2.shape import to_shape
from sqlalchemy import select, func, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from config.const import COORDS_SYSTEM_2D
from config.settings import Settings
from domain.models import Company, Building, Phone, Activity, CompanySummary
from domain.repositories import ICompanyRepository
from infrastructure.models.models import (
    CompanyOrm,
    BuildingOrm,
    ActivityOrm,
    company_activity,
)


class CompanyRepository(ICompanyRepository):
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def get_by_id(self, company_id: int) -> Company | None:
        query = (
            select(CompanyOrm)
            .where(CompanyOrm.id == company_id)
            .options(
                selectinload(CompanyOrm.phones),
                selectinload(CompanyOrm.activities),
                selectinload(CompanyOrm.building),
            )
        )
        async with self.session() as session:
            result = await session.execute(query)
        company_orm = result.scalar_one_or_none()

        if not company_orm:
            return None

        point = to_shape(company_orm.building.coordinates)

        return Company(
            id=company_orm.id,
            name=company_orm.name,
            legal_form=company_orm.legal_form,
            building=Building(
                id=company_orm.building.id,
                address=company_orm.building.address,
                latitude=point.x,
                longitude=point.y,
            ),
            phones=[Phone(id=phone.id, number=phone.number) for phone in company_orm.phones],
            activities=[
                Activity(
                    id=activity.id,
                    name=activity.name,
                    parent_id=activity.parent_id,
                )
                for activity in sorted(company_orm.activities, key=attrgetter("id"))
            ],
        )

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
    ) -> tuple[list[CompanySummary], int]:
        async with self.session() as session:
            query = (
                select(CompanyOrm)
                .options(selectinload(CompanyOrm.building))
                .limit(self.settings.company_items_per_page)
                .offset(offset)
            )
            count_query = select(func.count()).select_from(CompanyOrm)

            conditions = []

            # search by building
            if building_id is not None:
                conditions.append(CompanyOrm.building_id == building_id)

            # search by name
            if name:
                conditions.append(CompanyOrm.name.ilike(f"%{name}%"))

            # search by geo point and radius
            if lat is not None and lng is not None and radius is not None:
                point = func.ST_MakePoint(lng, lat)
                subq = select(BuildingOrm.id).where(ST_DWithin(BuildingOrm.coordinates, point, radius))
                conditions.append(CompanyOrm.building_id.in_(subq))

            # search by geo square
            if all(v is not None for v in (latx, lngx, laty, lngy)):
                from shapely import Polygon
                from geoalchemy2 import WKTElement

                polygon = Polygon(
                    [
                        (lngx, latx),
                        (lngx, laty),
                        (lngy, laty),
                        (lngy, latx),
                        (lngx, latx),
                    ]
                )

                polygon_wkt = WKTElement(polygon.wkt, srid=COORDS_SYSTEM_2D, extended=True)
                subq = select(BuildingOrm.id).where(
                    func.ST_Covers(
                        polygon_wkt,
                        BuildingOrm.coordinates,
                    )
                )
                conditions.append(CompanyOrm.building_id.in_(subq))

            # search by activity/activities
            if activity_id is not None:
                activity_ids = [activity_id]
                if activity_children:
                    activity_ids += await self._get_descendant_activity_ids(
                        root_id=activity_id, depth=2, session=session
                    )
                subq = select(company_activity.c.company_id).where(company_activity.c.activity_id.in_(activity_ids))
                conditions.append(CompanyOrm.id.in_(subq))

            if len(conditions) > 1:
                query = query.where(and_(*conditions))
                count_query = count_query.where(and_(*conditions))
            elif len(conditions) > 0:
                query = query.where(conditions[0])
                count_query = count_query.where(conditions[0])

            result = await session.execute(query)
            companies = result.scalars().all()

            count_result = await session.execute(count_query)
            total = count_result.scalar_one()
            domain_companies = [
                CompanySummary(
                    id=c.id,
                    name=c.name,
                    legal_form=c.legal_form,
                )
                for c in companies
            ]
        return domain_companies, total

    async def _get_descendant_activity_ids(self, root_id: int, depth: int, session: AsyncSession) -> list[int]:
        base = select(ActivityOrm.id, literal(1).label("level")).where(ActivityOrm.parent_id == root_id)

        activity_cte = base.cte(name="activity_tree", recursive=True)

        activity_alias = aliased(ActivityOrm)

        recursive = select(activity_alias.id, (activity_cte.c.level + 1).label("level")).where(
            activity_alias.parent_id == activity_cte.c.id, activity_cte.c.level < depth
        )

        activity_cte = activity_cte.union_all(recursive)

        query = select(activity_cte.c.id)

        result = await session.execute(query)
        ids = [row[0] for row in result.all()]
        return ids
