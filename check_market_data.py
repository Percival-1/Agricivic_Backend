import asyncio
from sqlalchemy import select, func
from app.database import AsyncSessionLocal
from app.models.market import MarketPrice


async def check_data():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(func.count(MarketPrice.id)))
        total = result.scalar()
        print(f"Total: {total}")

        result = await session.execute(
            select(MarketPrice)
            .where(MarketPrice.crop_name == "Wheat")
            .where(MarketPrice.state == "Delhi")
            .limit(5)
        )
        records = result.scalars().all()

        print(f"Wheat in Delhi: {len(records)}")
        for r in records:
            print(f"  {r.mandi_name}: Rs{r.price_per_quintal} on {r.date}")


asyncio.run(check_data())
