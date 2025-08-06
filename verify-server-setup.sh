#!/bin/bash

# Verification script for server setup

echo "Verifying server setup for backend deployment..."

# Check if docker-compose.server.yml exists
echo "1. Checking for docker-compose.server.yml..."
if [ -f "docker-compose.server.yml" ]; then
  echo "   ✓ docker-compose.server.yml found"
else
  echo "   ✗ docker-compose.server.yml not found"
fi

# Check if required environment variables are set in docker-compose
echo "2. Checking environment variables in docker-compose.server.yml..."
if grep -q "WEBAPP_URL.*12ef1c8f81ac.ngrok-free.app" docker-compose.server.yml; then
  echo "   ✓ WEBAPP_URL is set to ngrok URL"
else
  echo "   ✗ WEBAPP_URL is not set to ngrok URL"
fi

if grep -q "BACKEND_URL.*185.36.141.151:8001" docker-compose.server.yml; then
  echo "   ✓ BACKEND_URL is set to server IP"
else
  echo "   ✗ BACKEND_URL is not set to server IP"
fi

if grep -q "12ef1c8f81ac.ngrok-free.app" docker-compose.server.yml; then
  echo "   ✓ CORS is configured for ngrok URL"
else
  echo "   ✗ CORS is not configured for ngrok URL"
fi

# Check if required ports are exposed
echo "3. Checking exposed ports..."
if grep -q "8001:8001" docker-compose.server.yml; then
  echo "   ✓ Port 8001 is exposed for backend"
else
  echo "   ✗ Port 8001 is not exposed for backend"
fi

if grep -q "5435:5432" docker-compose.server.yml; then
  echo "   ✓ Port 5435 is exposed for database"
else
  echo "   ✗ Port 5435 is not exposed for database"
fi

echo "\nServer setup verification completed."
