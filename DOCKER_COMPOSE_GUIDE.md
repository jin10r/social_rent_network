# Docker Compose Configuration Guide

This project includes two separate docker-compose configurations for different deployment scenarios.

## 1. Server Deployment (Backend + Database)

File: `docker-compose.server.yml`

This configuration runs the backend API and PostgreSQL database on a server.

### Usage:

```bash
# Start services
docker-compose -f docker-compose.server.yml up -d

# Stop services
docker-compose -f docker-compose.server.yml down

# View logs
docker-compose -f docker-compose.server.yml logs -f
```

### Services included:
- `db`: PostgreSQL with PostGIS extension
- `backend`: Python FastAPI application

### Environment Variables:
Create a `.env` file in the project root with:

```
# Database Configuration
DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent

# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token
WEBAPP_URL=https://12ef1c8f81ac.ngrok-free.app
BACKEND_URL=http://185.36.141.151:8001

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,https://12ef1c8f81ac.ngrok-free.app
```

## 2. Local Development (Frontend with Ngrok)

File: `docker-compose.local.yml`

This configuration runs only the frontend for local development. It's designed to work with ngrok for external access.

### Prerequisites:
1. Ensure the backend is running and accessible (either locally or on a server)
2. Set the `REACT_APP_BACKEND_URL` environment variable to point to your backend

### Usage:

```bash
# Start frontend
docker-compose -f docker-compose.local.yml up -d

# Stop frontend
docker-compose -f docker-compose.local.yml down
```

### Environment Variables:
Create a `.env` file in the project root with:

```
# Backend API Configuration
REACT_APP_BACKEND_URL=http://185.36.141.151:8001
REACT_APP_BOT_USERNAME=your_bot_username
```

### Using with Ngrok:

The backend is already configured to work with your ngrok URL (https://12ef1c8f81ac.ngrok-free.app).

1. Start the server deployment:
   ```bash
   docker-compose -f docker-compose.server.yml up -d
   ```

2. Start the frontend locally:
   ```bash
   docker-compose -f docker-compose.local.yml up -d
   ```

3. Expose the frontend with ngrok (optional, for external access):
   ```bash
   ngrok http 3000
   ```

The frontend is already configured to connect to your backend at http://185.36.141.151:8001.

## Ensuring Synchronization

To ensure proper synchronization between frontend and backend:

1. The backend CORS configuration allows requests from the frontend origin
2. The frontend is configured with the correct backend URL
3. Both services are on the same Docker network when running together
4. Environment variables are properly set for both services

## Notes:

- The server deployment uses the internal database URL for communication between services
- The local deployment expects the backend to be accessible via the configured URL
- Adjust ports and environment variables as needed for your specific setup
- For production deployment, use specific origins in ALLOWED_ORIGINS instead of wildcards
