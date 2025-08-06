#!/bin/bash

# Test script to verify frontend-backend connection with specific configurations

echo "Testing connection between frontend and backend with specific configurations..."

# Test if backend is accessible at the specific IP
echo "1. Testing backend accessibility at 185.36.141.151:8001..."
if curl -s --connect-timeout 5 http://185.36.141.151:8001/docs > /dev/null; then
  echo "   ✓ Backend is accessible at http://185.36.141.151:8001"
else
  echo "   ⚠ Backend is NOT currently accessible at http://185.36.141.151:8001 (may not be running yet)"
fi

# Test if frontend is configured to connect to the correct backend
echo "2. Checking frontend configuration..."
if grep -q "REACT_APP_BACKEND_URL.*185.36.141.151:8001" docker-compose.local.yml; then
  echo "   ✓ Frontend is configured to connect to http://185.36.141.151:8001"
else
  echo "   ✗ Frontend is NOT configured to connect to http://185.36.141.151:8001"
  echo "   Current configuration:"
  grep "REACT_APP_BACKEND_URL" docker-compose.local.yml
fi

# Test CORS configuration for the ngrok URL
echo "3. Checking CORS configuration for ngrok URL..."
if grep -q "12ef1c8f81ac.ngrok-free.app" docker-compose.server.yml; then
  echo "   ✓ CORS is configured for https://12ef1c8f81ac.ngrok-free.app"
else
  echo "   ✗ CORS is NOT configured for https://12ef1c8f81ac.ngrok-free.app"
fi

echo "\nConnection test completed."
