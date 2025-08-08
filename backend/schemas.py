from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# User schemas
class UserBase(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    age: Optional[int] = Field(None, ge=18, le=100)
    bio: Optional[str] = None
    price_min: Optional[int] = Field(None, ge=0)
    price_max: Optional[int] = Field(None, ge=0)
    metro_station: Optional[str] = None
    search_radius: Optional[int] = Field(None, gt=0)
    
    @validator('price_max')
    def price_max_must_be_greater_than_min(cls, v, values):
        if v is not None and values.get('price_min') is not None:
            if v < values['price_min']:
                raise ValueError('price_max must be greater than or equal to price_min')
        return v

class UserCreate(UserBase):
    telegram_id: int
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude must be between -90 and 90")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Longitude must be between -180 and 180")

class UserUpdate(UserBase):
    lat: Optional[float] = Field(None, ge=-90, le=90, description="Latitude must be between -90 and 90")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="Longitude must be between -180 and 180")

class UserResponse(UserBase):
    id: UUID
    telegram_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileResponse(UserBase):
    id: UUID
    distance: Optional[float] = None  # Distance in km from current user
    
    class Config:
        from_attributes = True

# Listing schemas
class ListingBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: int = Field(ge=0)
    address: Optional[str] = None
    rooms: Optional[int] = Field(None, gt=0)
    area: Optional[float] = Field(None, gt=0)
    floor: Optional[int] = None
    total_floors: Optional[int] = None
    metro_station: Optional[str] = None
    metro_distance: Optional[int] = None
    photos: Optional[List[str]] = None

class ListingCreate(ListingBase):
    lat: float = Field(ge=-90, le=90, description="Latitude must be between -90 and 90")
    lon: float = Field(ge=-180, le=180, description="Longitude must be between -180 and 180")

class ListingResponse(ListingBase):
    id: UUID
    lat: float
    lon: float
    distance: Optional[float] = None  # Distance in km from search point
    is_liked: Optional[bool] = False
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Like and Match schemas
class LikeUserRequest(BaseModel):
    user_id: UUID

class MatchResponse(BaseModel):
    id: UUID
    user: UserProfileResponse
    created_at: datetime
    
    class Config:
        from_attributes = True

# Location schema
class LocationPoint(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)