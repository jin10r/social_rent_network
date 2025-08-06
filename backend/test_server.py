from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
import json
import hashlib
import hmac
import urllib.parse
from datetime import datetime, timedelta
import uuid

# Import test database
from test_database import (
    get_database, init_test_database, create_test_data,
    User, Listing, UserLike, ListingLike, async_session_maker
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic schemas
class UserCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    metro_station: Optional[str] = None
    search_radius: Optional[int] = None

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    bio: Optional[str] = None
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    metro_station: Optional[str] = None
    search_radius: Optional[int] = None

class UserResponse(BaseModel):
    id: str
    telegram_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    age: Optional[int]
    bio: Optional[str]
    price_min: Optional[int]
    price_max: Optional[int]
    metro_station: Optional[str]
    search_radius: Optional[int]
    is_active: bool

class ListingResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: int
    address: Optional[str]
    rooms: Optional[int]
    area: Optional[float]
    floor: Optional[int]
    total_floors: Optional[int]
    metro_station: Optional[str]
    metro_distance: Optional[int]

# Simple Telegram auth verification (simplified for testing)
def verify_telegram_data(init_data: str) -> dict:
    """Simplified Telegram auth verification for testing"""
    try:
        # Parse the init_data
        parsed_data = urllib.parse.parse_qs(init_data)
        
        # For testing, create a mock user
        mock_user = {
            'id': 123456789,
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser'
        }
        return mock_user
    except Exception as e:
        logger.error(f"Auth error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication data"
        )

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_database)
) -> User:
    """Get current user from database or create if not exists"""
    if not authorization:
        # For testing, create a default user
        telegram_user = {'id': 123456789, 'first_name': 'Test', 'last_name': 'User'}
    else:
        init_data = authorization.replace('Bearer ', '')
        telegram_user = verify_telegram_data(init_data)
    
    # Find or create user in database
    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.telegram_id == telegram_user['id'])
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            telegram_id=telegram_user['id'],
            first_name=telegram_user.get('first_name'),
            last_name=telegram_user.get('last_name'),
            username=telegram_user.get('username')
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    return user

# Initialize FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application startup: Initializing test database...")
    await init_test_database()
    
    # Create test data
    logger.info("Application startup: Creating test data...")
    await create_test_data()
    
    logger.info("Application startup completed")
    yield
    # Shutdown
    logger.info("Application shutdown")

app = FastAPI(
    title="Social Rent API (Test)",
    description="Test API for Telegram housing social network",
    version="1.0.0-test",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
async def root():
    return {"message": "Social Rent Test API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "sqlite", "test_mode": True}

# Metro stations endpoints (simplified)
@app.get("/api/metro/stations")
async def get_metro_stations():
    """Get metro stations for testing"""
    return ["Тверская", "Маяковская", "Пушкинская", "Чеховская", "Охотный ряд"]

@app.get("/api/metro/search")
async def search_metro(query: str = ""):
    """Search metro stations by query"""
    stations = ["Тверская", "Маяковская", "Пушкинская", "Чеховская"]
    filtered = [s for s in stations if query.lower() in s.lower()]
    return [{"name": station, "line": "Сокольническая", "color": "#red"} for station in filtered]

# User endpoints
@app.post("/api/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Create or update user profile"""
    # Update current user with provided data
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        age=current_user.age,
        bio=current_user.bio,
        price_min=current_user.price_min,
        price_max=current_user.price_max,
        metro_station=current_user.metro_station,
        search_radius=current_user.search_radius,
        is_active=current_user.is_active
    )

@app.get("/api/users/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return UserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        age=current_user.age,
        bio=current_user.bio,
        price_min=current_user.price_min,
        price_max=current_user.price_max,
        metro_station=current_user.metro_station,
        search_radius=current_user.search_radius,
        is_active=current_user.is_active
    )

@app.put("/api/users/profile", response_model=UserResponse)
async def update_user_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Update current user profile"""
    logger.info(f"Updating profile for user {current_user.id}")
    logger.info(f"Update data: {user_data.dict(exclude_unset=True)}")
    
    # Update user fields
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    await db.commit()
    await db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        age=current_user.age,
        bio=current_user.bio,
        price_min=current_user.price_min,
        price_max=current_user.price_max,
        metro_station=current_user.metro_station,
        search_radius=current_user.search_radius,
        is_active=current_user.is_active
    )

@app.get("/api/users/potential-matches", response_model=List[UserResponse])
async def get_potential_matches(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get potential matches"""
    from sqlalchemy import select
    
    # Get other users (simplified matching)
    result = await db.execute(
        select(User).where(
            User.id != current_user.id,
            User.is_active == True
        ).limit(limit)
    )
    users = result.scalars().all()
    
    return [
        UserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            age=user.age,
            bio=user.bio,
            price_min=user.price_min,
            price_max=user.price_max,
            metro_station=user.metro_station,
            search_radius=user.search_radius,
            is_active=user.is_active
        ) for user in users
    ]

@app.post("/api/users/{user_id}/like")
async def like_user(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Like another user"""
    # Check if like already exists
    from sqlalchemy import select
    
    existing_like = await db.execute(
        select(UserLike).where(
            UserLike.liker_id == current_user.id,
            UserLike.liked_id == user_id
        )
    )
    
    if existing_like.scalar_one_or_none():
        return {"message": "User already liked", "match": False}
    
    # Create like
    like = UserLike(liker_id=current_user.id, liked_id=user_id)
    db.add(like)
    
    # Check for mutual like (simplified)
    mutual_like = await db.execute(
        select(UserLike).where(
            UserLike.liker_id == user_id,
            UserLike.liked_id == current_user.id
        )
    )
    
    is_match = mutual_like.scalar_one_or_none() is not None
    
    await db.commit()
    
    return {"message": "User liked successfully", "match": is_match}

# Listing endpoints
@app.get("/api/listings/", response_model=List[ListingResponse])
async def get_listings(
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_database)
):
    """Get listings with filters"""
    from sqlalchemy import select
    
    query = select(Listing).where(Listing.is_active == True)
    
    if price_min:
        query = query.where(Listing.price >= price_min)
    if price_max:
        query = query.where(Listing.price <= price_max)
    
    query = query.limit(limit)
    
    result = await db.execute(query)
    listings = result.scalars().all()
    
    return [
        ListingResponse(
            id=listing.id,
            title=listing.title,
            description=listing.description,
            price=listing.price,
            address=listing.address,
            rooms=listing.rooms,
            area=float(listing.area) if listing.area else None,
            floor=listing.floor,
            total_floors=listing.total_floors,
            metro_station=listing.metro_station,
            metro_distance=listing.metro_distance
        ) for listing in listings
    ]

@app.post("/api/listings/{listing_id}/like")
async def like_listing(
    listing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Like a listing"""
    from sqlalchemy import select
    
    # Check if like already exists
    existing_like = await db.execute(
        select(ListingLike).where(
            ListingLike.user_id == current_user.id,
            ListingLike.listing_id == listing_id
        )
    )
    
    if existing_like.scalar_one_or_none():
        return {"message": "Listing already liked"}
    
    # Create like
    like = ListingLike(user_id=current_user.id, listing_id=listing_id)
    db.add(like)
    await db.commit()
    
    return {"message": "Listing liked successfully"}

@app.get("/api/listings/liked", response_model=List[ListingResponse])
async def get_liked_listings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """Get current user's liked listings"""
    from sqlalchemy import select
    from sqlalchemy.orm import joinedload
    
    result = await db.execute(
        select(Listing)
        .join(ListingLike, Listing.id == ListingLike.listing_id)
        .where(ListingLike.user_id == current_user.id)
    )
    listings = result.scalars().all()
    
    return [
        ListingResponse(
            id=listing.id,
            title=listing.title,
            description=listing.description,
            price=listing.price,
            address=listing.address,
            rooms=listing.rooms,
            area=float(listing.area) if listing.area else None,
            floor=listing.floor,
            total_floors=listing.total_floors,
            metro_station=listing.metro_station,
            metro_distance=listing.metro_distance
        ) for listing in listings
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)