"""
Check if market prices have location data
"""

import asyncio
from sqlalchemy import select
from app.database import get_db
from app.models.market import MarketPrice


async def check_locations():
    """Check market price location data"""
    async for db in get_db():
        # Get a sample of market prices
        result = await db.execute(
            select(MarketPrice).where(MarketPrice.crop_name == "Wheat").limit(5)
        )
        prices = result.scalars().all()

        print(f"\nFound {len(prices)} Wheat prices:")
        for price in prices:
            print(f"\nMandi: {price.mandi_name}")
            print(f"  Crop: {price.crop_name}")
            print(f"  Price: ₹{price.price_per_quintal}/quintal")
            print(f"  Date: {price.date}")
            print(f"  Location: lat={price.location_lat}, lng={price.location_lng}")
            print(f"  District: {price.district}, State: {price.state}")
            print(f"  Address: {price.location_address}")

        # Count total prices with location data
        result = await db.execute(
            select(MarketPrice)
            .where(MarketPrice.location_lat.isnot(None))
            .where(MarketPrice.location_lng.isnot(None))
        )
        count_with_location = len(result.scalars().all())

        result = await db.execute(select(MarketPrice))
        total_count = len(result.scalars().all())

        print(f"\n\nTotal prices: {total_count}")
        print(f"Prices with location data: {count_with_location}")
        print(f"Percentage: {(count_with_location/total_count*100):.1f}%")

        break


if __name__ == "__main__":
    asyncio.run(check_locations())
