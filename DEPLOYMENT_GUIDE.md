# Deployment Guide

This guide explains how to deploy the application with the frontend and backend on separate servers.

## Backend Deployment (Server at 185.36.141.151)

1. Copy the project files to the server:
   ```bash
   scp -r . user@185.36.141.151:/path/to/project
   ```

2. SSH into the server:
   ```bash
   ssh user@185.36.141.151
   ```

3. Navigate to the project directory:
   ```bash
   cd /path/to/project
   ```

4. Create a `.env` file with the following content:
   ```
   # Database Configuration
   DATABASE_URL_INTERNAL=postgresql+asyncpg://postgres:postgres123@db:5432/social_rent
   DATABASE_URL_EXTERNAL=postgresql+asyncpg://postgres:postgres123@localhost:5435/social_rent
   
   # Telegram Bot Configuration
   BOT_TOKEN=your_actual_bot_token_here
   WEBAPP_URL=https://12ef1c8f81ac.ngrok-free.app
   BACKEND_URL=http://185.36.141.151:8001
   
   # CORS Configuration
   ALLOWED_ORIGINS=http://localhost:3000,https://12ef1c8f81ac.ngrok-free.app
   ```

5. Start the backend and database services:
   ```bash
   docker-compose -f docker-compose.server.yml up -d
   ```

6. Verify that the backend is running:
   ```bash
   curl http://185.36.141.151:8001/docs
   ```

## Frontend Deployment (Local Development)

1. Create a `.env` file in the project root with the following content:
   ```
   # Backend API Configuration
   REACT_APP_BACKEND_URL=http://185.36.141.151:8001
   REACT_APP_BOT_USERNAME=your_bot_username
   ```

2. Start the frontend service:
   ```bash
   docker-compose -f docker-compose.local.yml up -d
   ```

3. Access the frontend at http://localhost:3000

## Using Ngrok for External Access

If you want to make the frontend accessible from the internet:

1. Start ngrok to expose the frontend:
   ```bash
   ngrok http 3000
   ```

2. Note the ngrok URL provided (e.g., https://abcd-123-456-789-0.ngrok-free.app)

3. Update the backend CORS configuration to allow this origin if needed:
   ```
   # In your backend .env file, update ALLOWED_ORIGINS:
   ALLOWED_ORIGINS=http://localhost:3000,https://12ef1c8f81ac.ngrok-free.app,https://abcd-123-456-789-0.ngrok-free.app
   ```

4. Restart the backend service:
   ```bash
   docker-compose -f docker-compose.server.yml restart backend
   ```

## Testing the Connection

Run the test script to verify that everything is configured correctly:
```bash
./test-connection-specific.sh
```

## Troubleshooting

1. If the frontend cannot connect to the backend:
   - Verify that the backend is running at 185.36.141.151:8001
   - Check that the firewall allows connections on port 8001
   - Ensure the ALLOWED_ORIGINS in the backend includes the frontend origin

2. If CORS errors occur:
   - Check the ALLOWED_ORIGINS environment variable in the backend
   - Restart the backend service after making changes

3. If the database connection fails:
   - Verify the database credentials in the .env file
   - Check that the database service is running
   - Verify that port 5435 is accessible on the server (for external connections)
   - Check that the firewall allows connections on port 5435
