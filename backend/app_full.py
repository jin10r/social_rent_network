"""
Полноценное Flask API с базой данных для тестирования пользовательских взаимодействий
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import uuid
import random
import math
from datetime import datetime
from contextlib import contextmanager

# Create Flask app
app = Flask(__name__)
CORS(app, origins="*")

# Database path
DB_PATH = "/app/backend/social_rent.db"

@contextmanager
def get_db():
    """Контекстный менеджер для работы с базой данных"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Возвращать результаты как словари
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Инициализация базы данных"""
    with get_db() as conn:
        # Создаём таблицы
        conn.executescript('''
            -- Таблица пользователей
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                age INTEGER,
                bio TEXT,
                price_min INTEGER,
                price_max INTEGER,
                metro_station TEXT,
                search_lat REAL,
                search_lon REAL,
                search_radius INTEGER,  -- в метрах
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Таблица объявлений
            CREATE TABLE IF NOT EXISTS listings (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                price INTEGER NOT NULL,
                address TEXT,
                lat REAL NOT NULL,
                lon REAL NOT NULL,
                rooms INTEGER,
                area REAL,
                metro_station TEXT,
                metro_distance INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- Таблица лайков пользователей
            CREATE TABLE IF NOT EXISTS user_likes (
                id TEXT PRIMARY KEY,
                liker_id TEXT,
                liked_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (liker_id) REFERENCES users (id),
                FOREIGN KEY (liked_id) REFERENCES users (id),
                UNIQUE(liker_id, liked_id)
            );

            -- Таблица матчей
            CREATE TABLE IF NOT EXISTS user_matches (
                id TEXT PRIMARY KEY,
                user1_id TEXT,
                user2_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user1_id) REFERENCES users (id),
                FOREIGN KEY (user2_id) REFERENCES users (id)
            );

            -- Таблица лайков объявлений
            CREATE TABLE IF NOT EXISTS listing_likes (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                listing_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (listing_id) REFERENCES listings (id),
                UNIQUE(user_id, listing_id)
            );
        ''')
        conn.commit()
    print("✅ База данных инициализирована")

def calculate_distance(lat1, lon1, lat2, lon2):
    """Вычисление расстояния между двумя точками в метрах (формула Haversine)"""
    if not all([lat1, lon1, lat2, lon2]):
        return float('inf')
    
    # Радиус Земли в метрах
    R = 6371000  
    
    # Преобразование в радианы
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Разности координат
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Формула Haversine
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    return distance

def do_search_areas_intersect(user1, user2):
    """Проверка пересечения зон поиска двух пользователей"""
    if not all([user1['search_lat'], user1['search_lon'], user1['search_radius'],
                user2['search_lat'], user2['search_lon'], user2['search_radius']]):
        return False
    
    # Расстояние между центрами зон поиска
    distance = calculate_distance(
        user1['search_lat'], user1['search_lon'],
        user2['search_lat'], user2['search_lon']
    )
    
    # Зоны пересекаются, если расстояние меньше суммы радиусов
    return distance <= (user1['search_radius'] + user2['search_radius'])

# Инициализация БД при старте
init_database()

# ====================== ОСНОВНЫЕ ЭНДПОИНТЫ ======================

@app.route('/')
def root():
    return jsonify({"message": "Social Rent API (Full) is running"})

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "version": "full", "database": "SQLite"})

# ====================== ПОЛЬЗОВАТЕЛИ ======================

@app.route('/api/users/create', methods=['POST'])
def create_user():
    """Создание нового пользователя"""
    data = request.json
    
    user_id = str(uuid.uuid4())
    
    with get_db() as conn:
        conn.execute('''
            INSERT INTO users (id, telegram_id, username, first_name, last_name, age, bio, 
                             price_min, price_max, metro_station, search_lat, search_lon, search_radius)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('telegram_id'),
            data.get('username'),
            data.get('first_name'),
            data.get('last_name'),
            data.get('age'),
            data.get('bio'),
            data.get('price_min'),
            data.get('price_max'),
            data.get('metro_station'),
            data.get('search_lat'),
            data.get('search_lon'),
            data.get('search_radius')
        ))
        conn.commit()
    
    return jsonify({
        "message": "Пользователь создан",
        "user_id": user_id,
        "user": data
    })

@app.route('/api/users/<user_id>')
def get_user(user_id):
    """Получение профиля пользователя"""
    with get_db() as conn:
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        return jsonify(dict(user))

@app.route('/api/users')
def get_all_users():
    """Получение всех пользователей"""
    with get_db() as conn:
        users = conn.execute('SELECT * FROM users WHERE is_active = 1').fetchall()
        return jsonify([dict(user) for user in users])

@app.route('/api/users/<user_id>/potential-matches')
def get_potential_matches(user_id):
    """Получение потенциальных матчей для пользователя"""
    with get_db() as conn:
        # Получаем текущего пользователя
        current_user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        if not current_user:
            return jsonify({"error": "Пользователь не найден"}), 404
        
        # Получаем всех других пользователей
        other_users = conn.execute('''
            SELECT * FROM users 
            WHERE id != ? AND is_active = 1
        ''', (user_id,)).fetchall()
        
        # Получаем уже лайкнутых пользователей
        liked_users = conn.execute('''
            SELECT liked_id FROM user_likes WHERE liker_id = ?
        ''', (user_id,)).fetchall()
        liked_user_ids = {row['liked_id'] for row in liked_users}
        
        potential_matches = []
        for user in other_users:
            # Пропускаем уже лайкнутых
            if user['id'] in liked_user_ids:
                continue
            
            # Проверяем пересечение зон поиска
            if do_search_areas_intersect(dict(current_user), dict(user)):
                user_dict = dict(user)
                user_dict['intersection_reason'] = 'search_areas_overlap'
                potential_matches.append(user_dict)
        
        return jsonify({
            "current_user_id": user_id,
            "potential_matches": potential_matches,
            "count": len(potential_matches)
        })

# ====================== ЛАЙКИ ======================

@app.route('/api/users/<user_id>/like', methods=['POST'])
def like_user(user_id):
    """Лайк пользователя"""
    data = request.json
    liker_id = data.get('liker_id')
    
    if not liker_id:
        return jsonify({"error": "liker_id обязателен"}), 400
    
    # Проверка, что пользователи существуют
    with get_db() as conn:
        liker = conn.execute('SELECT id FROM users WHERE id = ?', (liker_id,)).fetchone()
        liked = conn.execute('SELECT id FROM users WHERE id = ?', (user_id,)).fetchone()
        
        if not liker or not liked:
            return jsonify({"error": "Один из пользователей не найден"}), 404
        
        # Проверяем, есть ли уже лайк
        existing_like = conn.execute('''
            SELECT id FROM user_likes WHERE liker_id = ? AND liked_id = ?
        ''', (liker_id, user_id)).fetchone()
        
        if existing_like:
            return jsonify({"message": "Лайк уже существует", "match": False})
        
        # Добавляем лайк
        like_id = str(uuid.uuid4())
        conn.execute('''
            INSERT INTO user_likes (id, liker_id, liked_id)
            VALUES (?, ?, ?)
        ''', (like_id, liker_id, user_id))
        
        # Проверяем взаимный лайк (матч)
        mutual_like = conn.execute('''
            SELECT id FROM user_likes WHERE liker_id = ? AND liked_id = ?
        ''', (user_id, liker_id)).fetchone()
        
        is_match = bool(mutual_like)
        
        # Если матч, создаём запись в user_matches
        if is_match:
            match_id = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO user_matches (id, user1_id, user2_id)
                VALUES (?, ?, ?)
            ''', (match_id, liker_id, user_id))
        
        conn.commit()
    
    return jsonify({
        "message": "Лайк добавлен",
        "like_id": like_id,
        "match": is_match,
        "liker_id": liker_id,
        "liked_id": user_id
    })

@app.route('/api/users/<user_id>/matches')
def get_user_matches(user_id):
    """Получение матчей пользователя"""
    with get_db() as conn:
        matches = conn.execute('''
            SELECT m.*, 
                   u1.first_name as user1_name, u1.username as user1_username,
                   u2.first_name as user2_name, u2.username as user2_username
            FROM user_matches m
            JOIN users u1 ON m.user1_id = u1.id
            JOIN users u2 ON m.user2_id = u2.id
            WHERE m.user1_id = ? OR m.user2_id = ?
        ''', (user_id, user_id)).fetchall()
        
        return jsonify({
            "user_id": user_id,
            "matches": [dict(match) for match in matches],
            "count": len(matches)
        })

# ====================== ТЕСТОВЫЕ ДАННЫЕ ======================

@app.route('/api/test/create-users', methods=['POST'])
def create_test_users():
    """Создание тестовых пользователей с разными локациями"""
    
    # Координаты станций метро Москвы
    metro_stations = [
        {"name": "Сокольники", "lat": 55.7885, "lon": 37.6798},
        {"name": "Красносельская", "lat": 55.7781, "lon": 37.6627},
        {"name": "Комсомольская", "lat": 55.7755, "lon": 37.6549},
        {"name": "Красные ворота", "lat": 55.7687, "lon": 37.6506},
        {"name": "Чистые пруды", "lat": 55.7647, "lon": 37.6434},
        {"name": "Лубянка", "lat": 55.7609, "lon": 37.6274},
        {"name": "Охотный ряд", "lat": 55.7565, "lon": 37.6149},
        {"name": "Библиотека им. Ленина", "lat": 55.7514, "lon": 37.6097}
    ]
    
    first_names = ["Александр", "Мария", "Дмитрий", "Анна", "Михаил", "Елена", "Алексей", "Ольга"]
    last_names = ["Иванов", "Петрова", "Сидоров", "Козлова", "Смирнов", "Новикова"]
    
    users_created = []
    
    with get_db() as conn:
        # Очищаем старые данные
        conn.execute('DELETE FROM user_likes')
        conn.execute('DELETE FROM user_matches') 
        conn.execute('DELETE FROM users')
        conn.commit()
        
        for i in range(10):  # Создаём 10 тестовых пользователей
            station = random.choice(metro_stations)
            
            # Добавляем случайное смещение к координатам (в радиусе ~2км)
            lat_offset = random.uniform(-0.02, 0.02)
            lon_offset = random.uniform(-0.02, 0.02)
            
            user_id = str(uuid.uuid4())
            user_data = {
                "id": user_id,
                "telegram_id": 100000 + i,
                "username": f"testuser{i}",
                "first_name": random.choice(first_names),
                "last_name": random.choice(last_names),
                "age": random.randint(20, 40),
                "bio": f"Тестовый пользователь {i}. Ищу жильё в Москве.",
                "price_min": random.randint(20000, 40000),
                "price_max": random.randint(50000, 100000),
                "metro_station": station["name"],
                "search_lat": station["lat"] + lat_offset,
                "search_lon": station["lon"] + lon_offset,
                "search_radius": random.randint(1000, 5000)  # Радиус 1-5 км
            }
            
            conn.execute('''
                INSERT INTO users (id, telegram_id, username, first_name, last_name, age, bio,
                                 price_min, price_max, metro_station, search_lat, search_lon, search_radius)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data["id"], user_data["telegram_id"], user_data["username"],
                user_data["first_name"], user_data["last_name"], user_data["age"],
                user_data["bio"], user_data["price_min"], user_data["price_max"],
                user_data["metro_station"], user_data["search_lat"],
                user_data["search_lon"], user_data["search_radius"]
            ))
            
            users_created.append(user_data)
        
        conn.commit()
    
    return jsonify({
        "message": "Тестовые пользователи созданы",
        "users_created": len(users_created),
        "users": users_created
    })

@app.route('/api/test/create-interactions')
def create_test_interactions():
    """Создание тестовых взаимодействий между пользователями"""
    
    with get_db() as conn:
        # Получаем всех пользователей
        users = conn.execute('SELECT id FROM users').fetchall()
        user_ids = [user['id'] for user in users]
        
        if len(user_ids) < 2:
            return jsonify({"error": "Недостаточно пользователей для создания взаимодействий"}), 400
        
        # Очищаем старые лайки и матчи
        conn.execute('DELETE FROM user_likes')
        conn.execute('DELETE FROM user_matches')
        
        likes_created = 0
        matches_created = 0
        
        # Создаём случайные лайки
        for _ in range(15):  # Создаём 15 случайных лайков
            liker_id = random.choice(user_ids)
            liked_id = random.choice(user_ids)
            
            # Избегаем самолайков
            if liker_id == liked_id:
                continue
            
            # Проверяем, нет ли уже такого лайка
            existing = conn.execute('''
                SELECT id FROM user_likes WHERE liker_id = ? AND liked_id = ?
            ''', (liker_id, liked_id)).fetchone()
            
            if existing:
                continue
            
            # Добавляем лайк
            like_id = str(uuid.uuid4())
            conn.execute('''
                INSERT INTO user_likes (id, liker_id, liked_id)
                VALUES (?, ?, ?)
            ''', (like_id, liker_id, liked_id))
            likes_created += 1
            
            # Проверяем взаимный лайк
            mutual_like = conn.execute('''
                SELECT id FROM user_likes WHERE liker_id = ? AND liked_id = ?
            ''', (liked_id, liker_id)).fetchone()
            
            if mutual_like:
                # Создаём матч
                match_id = str(uuid.uuid4())
                conn.execute('''
                    INSERT INTO user_matches (id, user1_id, user2_id)
                    VALUES (?, ?, ?)
                ''', (match_id, liker_id, liked_id))
                matches_created += 1
        
        conn.commit()
    
    return jsonify({
        "message": "Тестовые взаимодействия созданы",
        "likes_created": likes_created,
        "matches_created": matches_created
    })

# ====================== АНАЛИТИКА ======================

@app.route('/api/test/analyze-intersections')
def analyze_intersections():
    """Анализ пересечений зон поиска пользователей"""
    
    with get_db() as conn:
        users = conn.execute('SELECT * FROM users WHERE is_active = 1').fetchall()
        users = [dict(user) for user in users]
    
    if len(users) < 2:
        return jsonify({"error": "Недостаточно пользователей для анализа"}), 400
    
    intersections = []
    
    for i, user1 in enumerate(users):
        for j, user2 in enumerate(users[i+1:], i+1):
            distance = calculate_distance(
                user1['search_lat'], user1['search_lon'],
                user2['search_lat'], user2['search_lon']
            )
            
            intersects = do_search_areas_intersect(user1, user2)
            
            intersections.append({
                "user1": {
                    "id": user1['id'],
                    "name": f"{user1['first_name']} {user1['last_name']}",
                    "metro_station": user1['metro_station'],
                    "search_radius": user1['search_radius']
                },
                "user2": {
                    "id": user2['id'], 
                    "name": f"{user2['first_name']} {user2['last_name']}",
                    "metro_station": user2['metro_station'],
                    "search_radius": user2['search_radius']
                },
                "distance_between_centers": round(distance, 2),
                "search_areas_intersect": intersects,
                "combined_radius": user1['search_radius'] + user2['search_radius']
            })
    
    # Фильтруем только пересечения
    intersecting_pairs = [item for item in intersections if item['search_areas_intersect']]
    
    return jsonify({
        "total_pairs_analyzed": len(intersections),
        "intersecting_pairs": len(intersecting_pairs),
        "intersection_details": intersecting_pairs
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=True)