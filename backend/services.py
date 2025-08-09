from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text
from sqlalchemy.orm import selectinload
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_GeogFromText, ST_AsText
from models import User, Listing, UserLike, UserMatch, ListingLike
from schemas import UserCreate, UserUpdate, ListingResponse, UserProfileResponse, MatchResponse
from typing import List, Optional, Dict
import uuid
from datetime import datetime
from metro_stations import get_metro_station_info

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_update_user(self, telegram_id: int, user_data: UserCreate) -> User:
        """Create or update user profile"""
        # Check if user exists
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            # Update existing user
            for field, value in user_data.dict(exclude_unset=True, exclude={'telegram_id', 'lat', 'lon'}).items():
                setattr(existing_user, field, value)
            
            # Update location based on metro station or lat/lon
            if user_data.metro_station:
                station_info = get_metro_station_info(user_data.metro_station)
                if station_info:
                    location_text = f'POINT({station_info["lon"]} {station_info["lat"]})'
                    existing_user.search_location = func.ST_GeogFromText(location_text)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Updated user location to: {user_data.metro_station} -> {location_text}")
            elif user_data.lat is not None and user_data.lon is not None:
                location_text = f'POINT({user_data.lon} {user_data.lat})'
                existing_user.search_location = func.ST_GeogFromText(location_text)
            
            existing_user.updated_at = datetime.utcnow()
            await self.db.commit()
            await self.db.refresh(existing_user)
            return existing_user
        else:
            # Create new user
            user_dict = user_data.dict(exclude={'lat', 'lon'})
            new_user = User(**user_dict)
            
            # Set location based on metro station or lat/lon
            if user_data.metro_station:
                station_info = get_metro_station_info(user_data.metro_station)
                if station_info:
                    location_text = f'POINT({station_info["lon"]} {station_info["lat"]})'
                    new_user.search_location = func.ST_GeogFromText(location_text)
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.info(f"Set new user location to: {user_data.metro_station} -> {location_text}")
            elif user_data.lat is not None and user_data.lon is not None:
                location_text = f'POINT({user_data.lon} {user_data.lat})'
                new_user.search_location = func.ST_GeogFromText(location_text)
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            return new_user

    async def update_user(self, user_id: uuid.UUID, user_data: UserUpdate) -> User:
        """Update existing user"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"Updating user {user_id} with data: {user_data.dict(exclude_unset=True)}")
        
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise ValueError("User not found")
        
        logger.info(f"Found user: {user.telegram_id}, {user.first_name}")
        
        # Update fields
        for field, value in user_data.dict(exclude_unset=True, exclude={'lat', 'lon'}).items():
            logger.info(f"Setting {field} to {value}")
            setattr(user, field, value)
        
        # Update location based on metro station or lat/lon
        if user_data.metro_station:
            logger.info(f"Updating location based on metro station: {user_data.metro_station}")
            station_info = get_metro_station_info(user_data.metro_station)
            if station_info:
                location_text = f'POINT({station_info["lon"]} {station_info["lat"]})'
                user.search_location = func.ST_GeogFromText(location_text)
                logger.info(f"Set location to: {location_text}")
            else:
                logger.warning(f"Metro station not found: {user_data.metro_station}")
        elif user_data.lat is not None and user_data.lon is not None:
            logger.info(f"Updating location based on lat/lon: {user_data.lat}, {user_data.lon}")
            location_text = f'POINT({user_data.lon} {user_data.lat})'
            user.search_location = func.ST_GeogFromText(location_text)
            logger.info(f"Set location to: {location_text}")
        
        user.updated_at = datetime.utcnow()
        
        try:
            logger.info("Committing changes to database")
            await self.db.commit()
            logger.info("Refreshing user data")
            await self.db.refresh(user)
            logger.info("User updated successfully")
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            await self.db.rollback()
            raise
        
        return user

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Get user by telegram ID"""
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


class MatchingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_potential_matches(self, user_id: uuid.UUID, limit: int = 10) -> List[UserProfileResponse]:
        """Get potential matches based on overlapping search areas"""
        # Get current user
        current_user_stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(current_user_stmt)
        current_user = result.scalar_one_or_none()
        
        if not current_user or not current_user.search_location:
            return []

        # Get current user's location as text
        location_stmt = select(func.ST_AsText(current_user.search_location))
        loc_result = await self.db.execute(location_stmt)
        location_text = loc_result.scalar()
        
        # Find users with overlapping search areas
        # Users are potential matches if:
        # 1. Their search area overlaps with current user's search area
        # 2. Current user's search area overlaps with their search area
        # 3. They haven't been liked by current user yet
        # 4. They are active
        
        stmt = text("""
            SELECT u.*, 
                   ST_Distance(u.search_location, ST_GeogFromText(:current_location)) / 1000 as distance_km
            FROM users u
            WHERE u.id != :user_id 
              AND u.is_active = true
              AND u.search_location IS NOT NULL
              AND u.search_radius IS NOT NULL
              AND (
                  ST_DWithin(u.search_location, ST_GeogFromText(:current_location), u.search_radius)
                  OR ST_DWithin(ST_GeogFromText(:current_location), u.search_location, :current_radius)
              )
              AND u.id NOT IN (
                  SELECT liked_id FROM user_likes WHERE liker_id = :user_id
              )
            ORDER BY distance_km
            LIMIT :limit
        """)
        
        result = await self.db.execute(stmt, {
            'user_id': user_id,
            'current_location': location_text,
            'current_radius': current_user.search_radius or 1000,
            'limit': limit
        })
        
        users_data = result.fetchall()
        
        # Convert to UserProfileResponse
        matches = []
        for row in users_data:
            user_dict = dict(row._mapping)
            distance = user_dict.pop('distance_km', None)
            
            match = UserProfileResponse(
                id=user_dict['id'],
                username=user_dict['username'],
                first_name=user_dict['first_name'],
                last_name=user_dict['last_name'],
                photo_url=user_dict['photo_url'],
                age=user_dict['age'],
                bio=user_dict['bio'],
                price_min=user_dict['price_min'],
                price_max=user_dict['price_max'],
                metro_station=user_dict['metro_station'],
                search_radius=user_dict['search_radius'],
                distance=distance
            )
            matches.append(match)
        
        return matches

    async def like_user(self, liker_id: uuid.UUID, liked_id: uuid.UUID) -> Dict[str, any]:
        """Like another user, creates match if mutual"""
        # Check if like already exists
        existing_like_stmt = select(UserLike).where(
            and_(UserLike.liker_id == liker_id, UserLike.liked_id == liked_id)
        )
        result = await self.db.execute(existing_like_stmt)
        existing_like = result.scalar_one_or_none()
        
        if existing_like:
            return {"already_liked": True, "match": False}
        
        # Create like
        new_like = UserLike(liker_id=liker_id, liked_id=liked_id)
        self.db.add(new_like)
        
        # Check for mutual like and create match if found
        mutual_like_stmt = select(UserLike).where(
            and_(UserLike.liker_id == liked_id, UserLike.liked_id == liker_id)
        )
        result = await self.db.execute(mutual_like_stmt)
        mutual_like = result.scalar_one_or_none()
        
        # If mutual like exists, create a match
        if mutual_like:
            # Check if match already exists
            existing_match_stmt = select(UserMatch).where(
                or_(
                    and_(UserMatch.user1_id == liker_id, UserMatch.user2_id == liked_id),
                    and_(UserMatch.user1_id == liked_id, UserMatch.user2_id == liker_id)
                )
            )
            result = await self.db.execute(existing_match_stmt)
            existing_match = result.scalar_one_or_none()
            
            if not existing_match:
                # Create new match (ensure consistent ordering: smaller UUID first)
                user1_id = min(liker_id, liked_id)
                user2_id = max(liker_id, liked_id)
                new_match = UserMatch(user1_id=user1_id, user2_id=user2_id)
                self.db.add(new_match)
        
        await self.db.commit()
        
        return {
            "liked": True,
            "match": bool(mutual_like),
            "message": "It's a match! 🎉" if mutual_like else "Like sent!"
        }

    async def get_user_matches(self, user_id: uuid.UUID) -> List[MatchResponse]:
        """Get user's matches (mutual likes)"""
        stmt = select(UserMatch).options(
            selectinload(UserMatch.user1),
            selectinload(UserMatch.user2)
        ).where(
            or_(UserMatch.user1_id == user_id, UserMatch.user2_id == user_id)
        ).order_by(UserMatch.created_at.desc())
        
        result = await self.db.execute(stmt)
        matches = result.scalars().all()
        
        match_responses = []
        for match in matches:
            # Get the other user
            other_user = match.user2 if match.user1_id == user_id else match.user1
            
            user_profile = UserProfileResponse(
                id=other_user.id,
                username=other_user.username,
                first_name=other_user.first_name,
                last_name=other_user.last_name,
                photo_url=other_user.photo_url,
                age=other_user.age,
                bio=other_user.bio,
                price_min=other_user.price_min,
                price_max=other_user.price_max,
                metro_station=other_user.metro_station,
                search_radius=other_user.search_radius
            )
            
            match_response = MatchResponse(
                id=match.id,
                user=user_profile,
                created_at=match.created_at
            )
            match_responses.append(match_response)
        
        return match_responses

    async def are_users_matched(self, user1_id: uuid.UUID, user2_id: uuid.UUID) -> bool:
        """Check if two users are matched"""
        stmt = select(UserMatch).where(
            or_(
                and_(UserMatch.user1_id == user1_id, UserMatch.user2_id == user2_id),
                and_(UserMatch.user1_id == user2_id, UserMatch.user2_id == user1_id)
            )
        )
        result = await self.db.execute(stmt)
        match = result.scalar_one_or_none()
        return bool(match)


class ListingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def search_listings(
        self, 
        lat: float = None, 
        lon: float = None, 
        radius: int = 1000,
        price_min: int = None,
        price_max: int = None,
        limit: int = 50
    ) -> List[ListingResponse]:
        """Search listings based on location and filters"""
        
        query = select(Listing).where(Listing.is_active == True)
        
        # Location filter
        if lat is not None and lon is not None:
            search_point = func.ST_GeogFromText(f'POINT({lon} {lat})')
            query = query.where(
                ST_DWithin(Listing.location, search_point, radius)
            ).add_columns(
                (ST_Distance(Listing.location, search_point) / 1000).label('distance_km')
            ).order_by(
                ST_Distance(Listing.location, search_point)
            )
        
        # Price filters
        if price_min is not None:
            query = query.where(Listing.price >= price_min)
        if price_max is not None:
            query = query.where(Listing.price <= price_max)
        
        query = query.limit(limit)
        
        result = await self.db.execute(query)
        
        listings = []
        if lat is not None and lon is not None:
            # When location filter is applied, we get tuples with distance
            rows = result.fetchall()
            for row in rows:
                if isinstance(row, tuple) and len(row) > 1:
                    listing, distance = row[0], row[1]
                else:
                    listing = row[0]
                    distance = None
                
                # Extract coordinates  
                location_stmt = select(func.ST_AsText(listing.location))
                loc_result = await self.db.execute(location_stmt)
                location_text = loc_result.scalar()
                
                # Parse POINT(lon lat) format
                coords = location_text.replace('POINT(', '').replace(')', '').split()
                listing_lon, listing_lat = float(coords[0]), float(coords[1])
                
                listing_response = ListingResponse(
                    id=listing.id,
                    title=listing.title,
                    description=listing.description,
                    price=listing.price,
                    address=listing.address,
                    lat=listing_lat,
                    lon=listing_lon,
                    rooms=listing.rooms,
                    area=listing.area,
                    floor=listing.floor,
                    total_floors=listing.total_floors,
                    metro_station=listing.metro_station,
                    metro_distance=listing.metro_distance,
                    photos=listing.photos,
                    distance=distance,
                    is_active=listing.is_active,
                    created_at=listing.created_at
                )
                listings.append(listing_response)
        else:
            # Without location filter, we get just the listing objects
            result_listings = result.scalars().all()
            for listing in result_listings:
                # Extract coordinates
                location_stmt = select(func.ST_AsText(listing.location))
                loc_result = await self.db.execute(location_stmt)
                location_text = loc_result.scalar()
                
                # Parse POINT(lon lat) format
                coords = location_text.replace('POINT(', '').replace(')', '').split()
                listing_lon, listing_lat = float(coords[0]), float(coords[1])
                
                listing_response = ListingResponse(
                    id=listing.id,
                    title=listing.title,
                    description=listing.description,
                    price=listing.price,
                    address=listing.address,
                    lat=listing_lat,
                    lon=listing_lon,
                    rooms=listing.rooms,
                    area=listing.area,
                    floor=listing.floor,
                    total_floors=listing.total_floors,
                    metro_station=listing.metro_station,
                    metro_distance=listing.metro_distance,
                    photos=listing.photos,
                    is_active=listing.is_active,
                    created_at=listing.created_at
                )
                listings.append(listing_response)
        
        return listings

    async def get_listings_for_user(self, user: User) -> List[ListingResponse]:
        """Get listings based on user's search criteria"""
        if not user.search_location:
            return []
        
        # Extract coordinates from user location
        location_stmt = select(func.ST_AsText(user.search_location))
        result = await self.db.execute(location_stmt)
        location_text = result.scalar()
        coords = location_text.replace('POINT(', '').replace(')', '').split()
        user_lon, user_lat = float(coords[0]), float(coords[1])
        
        return await self.search_listings(
            lat=user_lat,
            lon=user_lon,
            radius=user.search_radius or 1000,
            price_min=user.price_min,
            price_max=user.price_max
        )

    async def like_listing(self, user_id: uuid.UUID, listing_id: uuid.UUID) -> Dict[str, any]:
        """Like a listing"""
        # Check if like already exists
        existing_like_stmt = select(ListingLike).where(
            and_(ListingLike.user_id == user_id, ListingLike.listing_id == listing_id)
        )
        result = await self.db.execute(existing_like_stmt)
        existing_like = result.scalar_one_or_none()
        
        if existing_like:
            return {"already_liked": True}
        
        # Create like
        new_like = ListingLike(user_id=user_id, listing_id=listing_id)
        self.db.add(new_like)
        await self.db.commit()
        
        return {"liked": True}

    async def get_user_liked_listings(self, user_id: uuid.UUID) -> List[ListingResponse]:
        """Get user's liked listings"""
        stmt = select(Listing).join(ListingLike).where(
            and_(ListingLike.user_id == user_id, Listing.is_active == True)
        ).order_by(ListingLike.created_at.desc())
        
        result = await self.db.execute(stmt)
        listings = result.scalars().all()
        
        listing_responses = []
        for listing in listings:
            # Extract coordinates
            location_stmt = select(func.ST_AsText(listing.location))
            loc_result = await self.db.execute(location_stmt)
            location_text = loc_result.scalar()
            
            coords = location_text.replace('POINT(', '').replace(')', '').split()
            listing_lon, listing_lat = float(coords[0]), float(coords[1])
            
            listing_response = ListingResponse(
                id=listing.id,
                title=listing.title,
                description=listing.description,
                price=listing.price,
                address=listing.address,
                lat=listing_lat,
                lon=listing_lon,
                rooms=listing.rooms,
                area=listing.area,
                floor=listing.floor,
                total_floors=listing.total_floors,
                metro_station=listing.metro_station,
                metro_distance=listing.metro_distance,
                photos=listing.photos,
                is_liked=True,
                is_active=listing.is_active,
                created_at=listing.created_at
            )
            listing_responses.append(listing_response)
        
        return listing_responses