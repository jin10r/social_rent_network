import asyncio
import random
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import func
from models import User
import os

fake = Faker('ru_RU')

# Moscow coordinates bounds
MOSCOW_BOUNDS = {
    'lat_min': 55.48,
    'lat_max': 55.95,
    'lon_min': 37.32,
    'lon_max': 37.85
}

# Sample metro stations in Moscow
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

# Sample bio descriptions
SAMPLE_BIOS = [
    "Ищу уютное место для жизни в Москве. Работаю в IT, люблю спорт и путешествия.",
    "Студентка МГУ, тихая и аккуратная, ищу комнату недалеко от университета.",
    "Молодой специалист, только переехал в Москву. Ищу квартиру в спальном районе.",
    "Работаю удаленно, ищу тихое место с хорошим интернетом.",
    "Семейная пара без детей, ищем двухкомнатную квартиру.",
    "Творческая личность, фрилансер, ищу вдохновляющее место для жизни.",
    "Спортсмен, ищу жилье рядом с фитнес-клубами и парками.",
    "Работаю в центре, хочу жить недалеко от работы или рядом с метро.",
    "Любитель культуры, ищу квартиру рядом с театрами и музеями.",
    "Активный образ жизни, ищу место с развитой инфраструктурой."
]

async def generate_users(count: int = 100):
    """Generate random user profiles"""
    
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent")
    engine = create_async_engine(DATABASE_URL)
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session_maker() as session:
        users = []
        
        # Base telegram_id start (should be unique)
        base_telegram_id = 100000000
        
        for i in range(count):
            # Random coordinates within Moscow
            lat = random.uniform(MOSCOW_BOUNDS['lat_min'], MOSCOW_BOUNDS['lat_max'])
            lon = random.uniform(MOSCOW_BOUNDS['lon_min'], MOSCOW_BOUNDS['lon_max'])
            
            # Generate user profile
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = fake.user_name()
            age = random.randint(18, 45)
            
            # Price range (Moscow rent prices in RUB)
            price_min = random.randint(20000, 60000)
            price_max = random.randint(price_min + 10000, price_min + 80000)
            
            # Search radius (100m to 5km)
            search_radius = random.randint(500, 5000)
            
            metro_station = random.choice(METRO_STATIONS)
            bio = random.choice(SAMPLE_BIOS)
            
            # Create user
            user = User(
                telegram_id=base_telegram_id + i,
                username=username,
                first_name=first_name,
                last_name=last_name,
                photo_url=f"https://picsum.photos/200/200?random={i}",
                age=age,
                bio=bio,
                price_min=price_min,
                price_max=price_max,
                metro_station=metro_station,
                search_location=func.ST_GeogFromText(f'POINT({lon} {lat})'),
                search_radius=search_radius,
                is_active=True
            )
            
            users.append(user)
            
            # Commit in batches of 20
            if len(users) >= 20:
                session.add_all(users)
                await session.commit()
                users = []
                print(f"Generated {i+1} users...")
        
        # Commit remaining users
        if users:
            session.add_all(users)
            await session.commit()
        
        print(f"✅ Successfully generated {count} users!")

if __name__ == "__main__":
    asyncio.run(generate_users(100))