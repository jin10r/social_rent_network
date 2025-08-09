# 🏠 Social Rent - Deployment Guide

## ✅ Current Status

✅ **Backend** (FastAPI): Unified API + static files server on port 8001  
✅ **Frontend** (React): Built and served from backend  
✅ **Database** (PostgreSQL + PostGIS): Fully configured and working  
✅ **Telegram Bot** (aiogram): Ready for WebApp integration  
✅ **Profile System**: Create/Load/Save/Edit functionality tested and working  

## 🚀 Production Environment Configuration

### 1. Environment Variables (.env)

```env
# PostgreSQL Database Configuration
POSTGRES_DB=social_rent
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
POSTGRES_VOLUME_NAME=social_rent_postgres_data
DOCKER_NETWORK_NAME=social_rent_network

DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent
DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent

# Telegram Bot Configuration
REACT_APP_BOT_USERNAME=SocialRentBot
BOT_TOKEN=8482163056:AAGYMcCmHUxvrzDXkBESZPGV_kGiUVHZh4I
WEBAPP_URL=https://f53cac6205b2.ngrok-free.app
BACKEND_URL=http://localhost:8001

# Environment
ENVIRONMENT=development

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://localhost:3000,https://f53cac6205b2.ngrok-free.app

# Security
SECRET_KEY=your_secret_key_here_change_in_production

# API Configuration
API_PREFIX=/api

# Logging
LOG_LEVEL=INFO

# Test data generation
GENERATE_TEST_DATA=false

# Ports Configuration
DB_EXTERNAL_PORT=5433
DB_INTERNAL_PORT=5432
BACKEND_PORT=8001
FRONTEND_PORT=3000

# Additional backend configuration for unified serving
APP_PORT=8001
```

### 2. Frontend Environment (.env in frontend directory)

```env
REACT_APP_BACKEND_URL=http://localhost:8001
REACT_APP_BOT_USERNAME=SocialRentBot
```

### 3. Supervisor Configuration

The application uses supervisor to manage services. The configuration is located at `/etc/supervisor/conf.d/supervisord.conf`:

```ini
[program:backend]
command=/root/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8001 --workers 1
directory=/app/backend
environment=PYTHONPATH="/app:/app/backend"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/backend.err.log
stdout_logfile=/var/log/supervisor/backend.out.log
stopsignal=TERM
stopwaitsecs=30
stopasgroup=true
killasgroup=true

[program:bot]
command=/root/.venv/bin/python main.py
directory=/app/bot
environment=PYTHONPATH="/app:/app/bot"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/bot.err.log
stdout_logfile=/var/log/supervisor/bot.out.log
stopsignal=TERM
stopwaitsecs=30
stopasgroup=true
killasgroup=true
```

## 🗄️ Database Setup

### PostgreSQL + PostGIS Installation & Configuration

```bash
# Install PostgreSQL and PostGIS
apt-get update && apt-get install -y postgresql postgresql-contrib postgis

# Start PostgreSQL
service postgresql start

# Create database and enable PostGIS
sudo -u postgres createdb social_rent
sudo -u postgres psql -d social_rent -c "CREATE EXTENSION postgis;"

# Set password for postgres user
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres123';"

# Update pg_hba.conf for password authentication
# File: /etc/postgresql/15/main/pg_hba.conf
# Change peer/scram-sha-256 to md5 for all local connections

# Restart PostgreSQL
service postgresql restart
```

### Database Schema

The application automatically creates the following tables via SQLAlchemy:

- `users` - User profiles with geospatial search locations
- `listings` - Housing listings with geospatial coordinates  
- `user_likes` - User-to-user likes for matching
- `user_matches` - Mutual matches between users
- `listing_likes` - User likes for specific listings

## 🌐 Unified Architecture

### Backend (Port 8001)

The FastAPI backend serves:
- **API endpoints**: `/api/*` (all backend functionality)
- **Static files**: React build files for frontend
- **Fallback routing**: All non-API routes serve React app

### Key API Endpoints

```
GET  /health                    - Health check
GET  /api/metro/stations       - List all metro stations
GET  /api/metro/search         - Search metro stations
POST /api/users/               - Create user profile  
GET  /api/users/me             - Get current user profile
PUT  /api/users/profile        - Update user profile
GET  /api/users/potential-matches - Get potential matches
POST /api/users/{id}/like      - Like a user
GET  /api/users/matches        - Get user matches
GET  /api/listings/search      - Search listings
```

## 🤖 Telegram Bot Integration

### Bot Setup

1. Create bot with @BotFather in Telegram
2. Configure webhook or polling mode
3. Set WebApp URL to your domain
4. The bot handles:
   - Welcome message with WebApp button
   - Profile updates notifications
   - Match notifications
   - Contact sharing

### WebApp Integration

The React frontend is designed as a Telegram WebApp:
- Uses Telegram WebApp JS API
- Authenticates via Telegram initData
- Integrates with Telegram UI colors and themes
- Supports haptic feedback and alerts

## 🧪 Testing Profile Functionality

### Backend API Testing

```bash
# Health check
curl http://localhost:8001/health

# Create user profile
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {\"id\": 123456789, \"first_name\": \"Test\", \"username\": \"testuser\"}" \
  -d '{
    "telegram_id": 123456789,
    "first_name": "Test User",
    "age": 25,
    "bio": "Test user bio",
    "metro_station": "Сокольники",
    "search_radius": 2000,
    "price_min": 30000,
    "price_max": 50000
  }' \
  http://localhost:8001/api/users/

# Get user profile
curl -X GET \
  -H "Authorization: Bearer {\"id\": 123456789, \"first_name\": \"Test\", \"username\": \"testuser\"}" \
  http://localhost:8001/api/users/me

# Update user profile
curl -X PUT \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {\"id\": 123456789, \"first_name\": \"Test\", \"username\": \"testuser\"}" \
  -d '{
    "first_name": "Updated Name",
    "bio": "Updated bio",
    "price_max": 60000
  }' \
  http://localhost:8001/api/users/profile

# Search metro stations
curl "http://localhost:8001/api/metro/search?query=Сокол"
```

### Automated Testing

Run the comprehensive test suite:

```bash
cd /app
python backend_test.py
```

**Test Results**: 8/10 tests pass
- ✅ Health Check
- ✅ Root Endpoint  
- ✅ API Documentation
- ✅ Metro Stations API
- ✅ Metro Search API
- ✅ Frontend HTML Serving
- ✅ Static Files Serving
- ✅ Database Connection
- ⚠️ Favicon & Manifest (non-critical)
- ⚠️ CORS Configuration (non-critical for same-origin)

## 🔧 Service Management

### Start/Stop Services

```bash
# Check status
supervisorctl status

# Restart all services
supervisorctl restart all

# Restart individual services  
supervisorctl restart backend
supervisorctl restart bot

# View logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/bot.err.log
```

### Build and Deploy Frontend

```bash
# Build React frontend
cd /app/frontend && yarn build

# Copy build files to backend static directory
cp -r /app/frontend/build/* /app/static/

# Restart backend to serve new files
supervisorctl restart backend
```

## 🔐 Security Considerations

### For Production Deployment:

1. **Change default passwords**: Update PostgreSQL password
2. **Update SECRET_KEY**: Use cryptographically secure secret  
3. **Configure CORS**: Restrict ALLOWED_ORIGINS to your domain
4. **Use HTTPS**: Configure SSL/TLS certificates
5. **Environment isolation**: Use separate production environment files
6. **Database security**: Configure proper user permissions and firewall rules

## 🎉 Success Criteria

✅ **Profile Management**: All CRUD operations working  
- Create new profiles ✓
- Load existing profiles ✓  
- Save profile changes ✓
- Edit profile fields ✓

✅ **Metro Station Autocomplete**: Working with 87+ Moscow metro stations  
✅ **Telegram WebApp Integration**: Bot ready for WebApp deployment  
✅ **Unified Architecture**: Single port (8001) serves both API and frontend  
✅ **Database**: PostgreSQL + PostGIS with geospatial capabilities  
✅ **Service Management**: All services managed by supervisor  

## 📱 Frontend Access

- **Local Development**: http://localhost:8001/profile
- **Production**: https://your-domain.com/profile  
- **Telegram WebApp**: Accessible via Telegram bot

The application is fully functional and ready for Telegram WebApp deployment!