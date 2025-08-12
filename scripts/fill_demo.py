import asyncio

from config.containers import Container
from infrastructure.tests.utils import create_demo_activities, create_demo_companies


async def main() -> None:
    container = Container()
    db = container.db()
    async with db.session() as session:
        activities = await create_demo_activities(db=session)
        await create_demo_companies(db=session, activities=activities)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
