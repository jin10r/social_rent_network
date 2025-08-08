import asyncio
import random
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, func
from models import User, UserLike
import os

async def create_test_matches():
    """Create some test matches for demonstration"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent")
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        # Get some random users
        stmt = select(User).limit(20)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        if len(users) < 4:
            print("Not enough users to create matches")
            return
        
        # Create some mutual likes (which will automatically create matches via trigger)
        matches_created = 0
        
        for i in range(0, len(users) - 1, 2):
            user1 = users[i]
            user2 = users[i + 1]
            
            # Create mutual likes
            like1 = UserLike(liker_id=user1.id, liked_id=user2.id)
            like2 = UserLike(liker_id=user2.id, liked_id=user1.id)
            
            session.add(like1)
            session.add(like2)
            matches_created += 1
            
            if matches_created >= 5:  # Create 5 matches
                break
        
        await session.commit()
        print(f"✅ Created {matches_created} test matches!")

if __name__ == "__main__":
    asyncio.run(create_test_matches())