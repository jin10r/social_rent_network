#!/usr/bin/env python3
"""
Скрипт для генерации тестовых данных для Social Rent App
Создает:
- 100 пользователей
- 1000 объявлений о недвижимости
"""
import asyncio
import asyncpg
import random
from faker import Faker
from datetime import datetime, timedelta
import uuid
from typing import List, Tuple

# Инициализация Faker для русской локали
fake = Faker('ru_RU')

# Координаты Москвы и области
MOSCOW_CENTER = (55.7558, 37.6176)
MOSCOW_BOUNDS = {
    'lat_min': 55.5,
    'lat_max': 56.0,
    'lon_min': 37.2,
    'lon_max': 37.9
}

# Список станций метро Москвы
METRO_STATIONS = [
    "Сокольники", "Красносельская", "Комсомольская", "Красные Ворота", "Чистые пруды",
    "Лубянка", "Охотный Ряд", "Библиотека им. Ленина", "Кропоткинская", "Парк культуры",
    "Фрунзенская", "Спортивная", "Воробьевы горы", "Университет", "Проспект Вернадского",
    "Тверская", "Театральная", "Новокузнецкая", "Павелецкая", "Автозаводская",
    "Коломенская", "Каширская", "Кантемировская", "Царицыно", "Орехово",
    "Арбатская", "Смоленская", "Киевская", "Студенческая", "Кутузовская",
    "Площадь Революции", "Курская", "Бауманская", "Электрозаводская", "Семеновская",
    "Партизанская", "Измайловская", "Первомайская", "Щукинская", "Тушинская",
    "Сходненская", "Планерная", "Алтуфьево", "Бибирево", "Отрадное",
    "Владыкино", "Петровско-Разумовская", "Тимирязевская", "Дмитровская", "Савеловская",
    "Менделеевская", "Цветной бульвар", "Трубная", "Сретенский бульвар", "Чкаловская",
    "Римская", "Крестьянская застава", "Дубровка", "Кожуховская", "Печатники",
    "Волжская", "Люблино", "Братиславская", "Марьино", "Борисово",
    "Шипиловская", "Зябликово", "Медведково", "Бабушкинская", "Свиблово",
    "Ботанический сад", "ВДНХ", "Алексеевская", "Рижская", "Проспект Мира",
    "Сухаревская", "Тургеневская", "Кузнецкий мост", "Пушкинская", "Баррикадная",
    "Белорусская", "Новослободская", "Проспект Мира", "Комсомольская", "Красносельская",
    "Сокольники", "Преображенская площадь", "Черкизовская", "Улица Подбельского", "Новогиреево",
    "Перово", "Шоссе Энтузиастов", "Авиамоторная", "Площадь Ильича", "Марксистская",
    "Третьяковская", "Октябрьская", "Добрынинская", "Павелецкая", "Таганская",
    "Пролетарская", "Волгоградский проспект", "Текстильщики", "Кузьминки", "Рязанский проспект",
    "Выхино", "Лермонтовский проспект", "Жулебино", "Котельники", "Лухмановская",
    "Некрасовка", "Юго-Восточная", "Косино", "Улица Дмитриевского", "Лесопарковая"
]

# Типичные адреса и районы Москвы
MOSCOW_DISTRICTS = [
    "Центральный", "Северный", "Северо-Восточный", "Восточный", "Юго-Восточный",
    "Южный", "Юго-Западный", "Западный", "Северо-Западный", "Зеленоград",
    "Новомосковский", "Троицкий"
]

def generate_moscow_coordinates() -> Tuple[float, float]:
    """Генерирует случайные координаты в пределах Москвы"""
    lat = random.uniform(MOSCOW_BOUNDS['lat_min'], MOSCOW_BOUNDS['lat_max'])
    lon = random.uniform(MOSCOW_BOUNDS['lon_min'], MOSCOW_BOUNDS['lon_max'])
    return lat, lon

def generate_user_data() -> dict:
    """Генерирует данные для одного пользователя"""
    age = random.randint(18, 45)
    
    # Генерируем бюджет в зависимости от возраста
    base_budget = random.randint(20000, 150000)
    price_min = base_budget - random.randint(0, 15000)
    price_max = base_budget + random.randint(10000, 50000)
    
    # Выбираем случайную станцию метро
    metro_station = random.choice(METRO_STATIONS)
    
    # Получаем координаты станции из справочника
    from metro_stations import get_metro_station_info
    station_info = get_metro_station_info(metro_station)
    
    if station_info:
        # Используем координаты из справочника
        lat, lon = station_info['lat'], station_info['lon']
        search_location = f'POINT({lon} {lat})'
    else:
        # Если станция не найдена в справочнике, генерируем случайные координаты
        lat, lon = generate_moscow_coordinates()
        search_location = f'POINT({lon} {lat})'
    
    return {
        'id': str(uuid.uuid4()),
        'telegram_id': random.randint(100000000, 999999999),
        'username': fake.user_name(),
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'photo_url': f"https://i.pravatar.cc/150?u={random.randint(1, 1000)}",
        'age': age,
        'bio': fake.text(max_nb_chars=200),
        'price_min': price_min,
        'price_max': price_max,
        'metro_station': metro_station,
        'search_location': search_location,
        'search_radius': random.choice([500, 1000, 1500, 2000, 3000, 5000]),
        'is_active': True,
        'created_at': fake.date_time_between(start_date='-30d', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-7d', end_date='now')
    }

def generate_listing_data() -> dict:
    """Генерирует данные для одного объявления"""
    rooms = random.randint(1, 4)
    
    # Генерируем цену в зависимости от количества комнат
    base_price = {1: 35000, 2: 55000, 3: 75000, 4: 95000}[rooms]
    price = base_price + random.randint(-15000, 25000)
    
    area = random.randint(25, 120)
    floor = random.randint(1, 25)
    total_floors = floor + random.randint(0, 10)
    
    # Типы объявлений
    apartment_types = [
        "Уютная квартира в центре",
        "Современная квартира с ремонтом",
        "Просторная квартира рядом с метро",
        "Квартира в новостройке",
        "Комфортная квартира для семьи",
        "Стильная квартира в тихом районе",
        "Светлая квартира с хорошим видом",
        "Квартира после евроремонта",
        "Квартира в престижном районе",
        "Уютная квартира для студентов"
    ]
    
    title = f"{rooms}-комн. квартира, {area} м²"
    if random.choice([True, False]):
        title = random.choice(apartment_types) + f", {rooms} комн."
    
    # Генерируем описание
    features = [
        "мебель включена", "бытовая техника", "балкон", "лоджия",
        "кондиционер", "интернет", "парковка", "охрана",
        "консьерж", "лифт", "после ремонта", "тихий двор",
        "развитая инфраструктура", "рядом школы и детские сады",
        "удобная транспортная развязка", "зеленая зона рядом"
    ]
    
    selected_features = random.sample(features, random.randint(2, 6))
    description = f"Сдается {rooms}-комнатная квартира площадью {area} м². " + \
                 f"Этаж {floor} из {total_floors}. " + \
                 "В квартире: " + ", ".join(selected_features) + ". " + \
                 fake.text(max_nb_chars=100)
    
    metro_station = random.choice(METRO_STATIONS)
    metro_distance = random.randint(200, 1500) * 50  # в метрах, кратно 50
    
    # Получаем координаты станции из справочника
    from metro_stations import get_metro_station_info
    station_info = get_metro_station_info(metro_station)
    
    if station_info:
        # Используем координаты станции как базовые, добавляем небольшое отклонение
        base_lat, base_lon = station_info['lat'], station_info['lon']
        # Добавляем случайное отклонение в пределах 2 км от станции
        lat = base_lat + random.uniform(-0.02, 0.02)  # примерно ±2 км по широте
        lon = base_lon + random.uniform(-0.02, 0.02)  # примерно ±2 км по долготе
    else:
        # Если станция не найдена, генерируем случайные координаты
        lat, lon = generate_moscow_coordinates()
    
    # Генерируем адрес
    street_names = [
        "ул. Тверская", "ул. Арбат", "ул. Пречистенка", "ул. Остоженка",
        "Ленинский проспект", "проспект Мира", "ул. Маросейка", "ул. Покровка",
        "ул. Мясницкая", "ул. Садовая", "ул. Большая Дмитровка", "ул. Никольская",
        "ул. Солянка", "ул. Варварка", "ул. Ильинка", "ул. Моховая",
        "Кутузовский проспект", "Ломоносовский проспект", "ул. Вавилова",
        "ул. Профсоюзная", "ул. Ленинская", "ул. Академика Королева"
    ]
    
    address = f"{random.choice(street_names)}, д. {random.randint(1, 99)}"
    if random.choice([True, False]):
        address += f", стр. {random.randint(1, 5)}"
    
    # Фотографии (мокап)
    photos = []
    num_photos = random.randint(3, 8)
    for i in range(num_photos):
        photos.append(f"https://picsum.photos/800/600?random={random.randint(1, 10000)}")
    
    return {
        'id': str(uuid.uuid4()),
        'title': title,
        'description': description,
        'price': price,
        'address': address,
        'location': f'POINT({lon} {lat})',
        'rooms': rooms,
        'area': area,
        'floor': floor,
        'total_floors': total_floors,
        'metro_station': metro_station,
        'metro_distance': metro_distance,
        'photos': photos,
        'is_active': True,
        'created_at': fake.date_time_between(start_date='-60d', end_date='now'),
        'updated_at': fake.date_time_between(start_date='-7d', end_date='now')
    }

async def create_users(conn, num_users: int = 1000):
    """Создает пользователей в базе данных"""
    print(f"Создание {num_users} пользователей...")
    
    users = []
    for i in range(num_users):
        user_data = generate_user_data()
        users.append((
            user_data['id'],
            user_data['telegram_id'],
            user_data['username'],
            user_data['first_name'],
            user_data['last_name'],
            user_data['photo_url'],
            user_data['age'],
            user_data['bio'],
            user_data['price_min'],
            user_data['price_max'],
            user_data['metro_station'],
            user_data['search_location'],
            user_data['search_radius'],
            user_data['is_active'],
            user_data['created_at'],
            user_data['updated_at']
        ))
        
        if (i + 1) % 20 == 0:
            print(f"  Подготовлено {i + 1}/{num_users} пользователей")
    
    # Вставляем всех пользователей одним запросом
    await conn.executemany(
        """
        INSERT INTO users (
            id, telegram_id, username, first_name, last_name, photo_url,
            age, bio, price_min, price_max, metro_station, search_location,
            search_radius, is_active, created_at, updated_at
        ) VALUES (
            $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 
            ST_GeogFromText($12), $13, $14, $15, $16
        )
        """,
        users
    )
    
    print(f"✅ Создано {num_users} пользователей")

async def create_listings(conn, num_listings: int = 1000):
    """Создает объявления в базе данных"""
    print(f"Создание {num_listings} объявлений...")
    
    # Создаем объявления батчами по 100
    batch_size = 100
    for batch_start in range(0, num_listings, batch_size):
        batch_end = min(batch_start + batch_size, num_listings)
        batch_listings = []
        
        for i in range(batch_start, batch_end):
            listing_data = generate_listing_data()
            batch_listings.append((
                listing_data['id'],
                listing_data['title'],
                listing_data['description'],
                listing_data['price'],
                listing_data['address'],
                listing_data['location'],
                listing_data['rooms'],
                listing_data['area'],
                listing_data['floor'],
                listing_data['total_floors'],
                listing_data['metro_station'],
                listing_data['metro_distance'],
                listing_data['photos'],
                listing_data['is_active'],
                listing_data['created_at'],
                listing_data['updated_at']
            ))
        
        # Вставляем батч
        await conn.executemany(
            """
            INSERT INTO listings (
                id, title, description, price, address, location, rooms, area,
                floor, total_floors, metro_station, metro_distance, photos,
                is_active, created_at, updated_at
            ) VALUES (
                $1, $2, $3, $4, $5, ST_GeogFromText($6), $7, $8, $9, $10,
                $11, $12, $13, $14, $15, $16
            )
            """,
            batch_listings
        )
        
        print(f"  Создано {batch_end}/{num_listings} объявлений")
    
    print(f"✅ Создано {num_listings} объявлений")

async def main():
    """Main function"""
    # Определяем DATABASE_URL в зависимости от среды выполнения
    import os
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres123@localhost:5433/social_rent")
    # Для совместимости с asyncpg убираем +asyncpg из URL
    if DATABASE_URL.startswith("postgresql+asyncpg://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    print("🚀 Запуск генерации тестовых данных для Social Rent App")
    print("=" * 50)
    
    try:
        # Подключение к базе данных
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Подключение к базе данных установлено")
        
        # Очищаем существующие данные
        print("\n🧹 Очистка существующих данных...")
        await conn.execute("DELETE FROM listing_likes")
        await conn.execute("DELETE FROM user_matches") 
        await conn.execute("DELETE FROM user_likes")
        await conn.execute("DELETE FROM listings")
        await conn.execute("DELETE FROM users")
        print("✅ Существующие данные очищены")
        
        # Создаем пользователей
        print("\n👥 Создание пользователей...")
        await create_users(conn, 1000)
        
        # Создаем объявления
        print("\n🏠 Создание объявлений...")
        await create_listings(conn, 1000)
        
        # Получаем статистику
        print("\n📊 Статистика созданных данных:")
        users_count = await conn.fetchval("SELECT COUNT(*) FROM users")
        listings_count = await conn.fetchval("SELECT COUNT(*) FROM listings")
        user_likes_count = await conn.fetchval("SELECT COUNT(*) FROM user_likes")
        matches_count = await conn.fetchval("SELECT COUNT(*) FROM user_matches")
        listing_likes_count = await conn.fetchval("SELECT COUNT(*) FROM listing_likes")
        
        print(f"  👥 Пользователи: {users_count}")
        print(f"  🏠 Объявления: {listings_count}")
        print(f"  💖 Лайки пользователей: {user_likes_count}")
        print(f"  🤝 Матчи: {matches_count}")
        print(f"  ⭐ Лайки объявлений: {listing_likes_count}")
        
        await conn.close()
        
        print("\n🎉 Генерация тестовых данных завершена успешно!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)