import asyncio
import random
from faker import Faker
from faker.providers import internet, lorem
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func
from models import Listing
import os
from datetime import datetime

fake = Faker('ru_RU')
fake.add_provider(internet)
fake.add_provider(lorem)

# Moscow coordinates bounds (approximately)
MOSCOW_BOUNDS = {
    'lat_min': 55.48,
    'lat_max': 55.95,
    'lon_min': 37.32,
    'lon_max': 37.85
}

# Moscow metro stations (sample)
METRO_STATIONS = [
    "Сокольники", "Красносельская", "Комсомольская", "Красные Ворота", "Чистые пруды",
    "Лубянка", "Охотный Ряд", "Библиотека им. Ленина", "Кропоткинская", "Парк Культуры",
    "Фрунзенская", "Спортивная", "Воробьевы горы", "Университет", "Проспект Вернадского",
    "Юго-Западная", "Тропарево", "Румянцево", "Саларьево", "Филатов Луг",
    "Прокшино", "Ольховая", "Коммунарка", "Ховрино", "Беломорская",
    "Речной вокзал", "Водный стадион", "Войковская", "Сокол", "Аэропорт",
    "Динамо", "Белорусская", "Новослободская", "Менделеевская", "Цветной бульвар",
    "Тверская", "Театральная", "Новокузнецкая", "Павелецкая", "Автозаводская",
    "Технопарк", "Коломенская", "Каширская", "Кантемировская", "Царицыно",
    "Орехово", "Домодедовская", "Красногвардейская", "Алма-Атинская", "Бульвар Рокоссовского"
]

# Sample room descriptions
ROOM_DESCRIPTIONS = [
    "Уютная студия в центре города",
    "Просторная однокомнатная квартира",
    "Светлая двухкомнатная квартира с ремонтом",
    "Трехкомнатная квартира в новостройке",
    "Современная квартира с панорамными окнами",
    "Квартира после евроремонта",
    "Уютная квартира рядом с метро",
    "Просторная квартира в тихом районе",
    "Квартира в доме бизнес-класса",
    "Стильная квартира с современным дизайном"
]

async def generate_listings(count: int = 1000):
    """Generate random apartment listings in Moscow"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent")
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        listings = []
        
        for i in range(count):
            # Random coordinates within Moscow
            lat = random.uniform(MOSCOW_BOUNDS['lat_min'], MOSCOW_BOUNDS['lat_max'])
            lon = random.uniform(MOSCOW_BOUNDS['lon_min'], MOSCOW_BOUNDS['lon_max'])
            
            # Random apartment details
            rooms = random.randint(1, 4)
            area = random.uniform(20, 150)
            floor = random.randint(1, 25)
            total_floors = max(floor, random.randint(floor, 30))
            
            # Price based on rooms and area (rough Moscow prices)
            base_price = rooms * 25000 + area * 300
            price = int(base_price * random.uniform(0.7, 1.5))
            
            metro_station = random.choice(METRO_STATIONS)
            metro_distance = random.randint(50, 1500)  # meters to metro
            
            # Generate address
            street_names = [
                "улица Тверская", "Ленинский проспект", "улица Арбат", "Кутузовский проспект",
                "Садовое кольцо", "улица Баумана", "проспект Мира", "Варшавское шоссе",
                "Ленинградский проспект", "Рублевское шоссе", "улица Пречистенка"
            ]
            street = random.choice(street_names)
            house_number = random.randint(1, 200)
            building = random.choice(['', 'А', 'Б', 'В', '1', '2'])
            address = f"{street}, {house_number}{building}"
            
            # Sample photos (placeholder URLs)
            photos = [
                f"https://picsum.photos/800/600?random={i}_1",
                f"https://picsum.photos/800/600?random={i}_2",
                f"https://picsum.photos/800/600?random={i}_3"
            ]
            
            # Create listing
            listing = Listing(
                title=f"{rooms}-комнатная квартира, {int(area)} м²",
                description=random.choice(ROOM_DESCRIPTIONS),
                price=price,
                address=address,
                location=func.ST_GeogFromText(f'POINT({lon} {lat})'),
                rooms=rooms,
                area=round(area, 1),
                floor=floor,
                total_floors=total_floors,
                metro_station=metro_station,
                metro_distance=metro_distance,
                photos=photos,
                is_active=True
            )
            
            listings.append(listing)
            
            # Commit in batches of 100
            if len(listings) >= 100:
                session.add_all(listings)
                await session.commit()
                listings = []
                print(f"Generated {i+1} listings...")
        
        # Commit remaining listings
        if listings:
            session.add_all(listings)
            await session.commit()
        
        print(f"Successfully generated {count} listings!")

if __name__ == "__main__":
    asyncio.run(generate_listings(1000))