#!/bin/bash

# Test script to verify frontend-backend connection

echo "Testing connection between frontend and backend..."

# Test if backend is accessible
echo "1. Testing backend accessibility..."
if curl -s http://localhost:8001/docs > /dev/null; then
  echo "   ✓ Backend is accessible at http://localhost:8001"
else
  echo "   ✗ Backend is NOT accessible at http://localhost:8001"
fi

# Test if frontend is accessible
echo "2. Testing frontend accessibility..."
if curl -s http://localhost:3000 > /dev/null; then
  echo "   ✓ Frontend is accessible at http://localhost:3000"
else
  echo "   ✗ Frontend is NOT accessible at http://localhost:3000"
fi

# Test CORS configuration
echo "3. Testing CORS configuration..."
if curl -s -H "Origin: http://localhost:3000" -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: X-Requested-With" -X OPTIONS http://localhost:8001/api/ > /dev/null; then
  echo "   ✓ CORS is properly configured for http://localhost:3000"
else
  echo "   ✗ CORS may not be properly configured for http://localhost:3000"
fi

echo "\nConnection test completed."
