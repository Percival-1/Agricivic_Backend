"""
Check if admin user exists
"""

import asyncio
from sqlalchemy import select
from app.database import get_db
from app.models.user import User


async def check_admin():
    """Check for admin users"""
    async for db in get_db():
        result = await db.execute(select(User).where(User.role == "admin"))
        admins = result.scalars().all()

        if admins:
            print(f"Found {len(admins)} admin user(s):\n")
            for admin in admins:
                print(f"  Phone: {admin.phone_number}")
                print(f"  Name: {admin.name}")
                print(f"  Active: {admin.is_active}")
                print(f"  ID: {admin.id}")
                print()
        else:
            print("No admin users found.")
            print("\nTo create an admin user, run:")
            print("  python create_admin_user.py")

        break


if __name__ == "__main__":
    asyncio.run(check_admin())
