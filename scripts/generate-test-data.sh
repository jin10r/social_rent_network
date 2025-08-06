#!/bin/bash

# Script to generate all test data
# Usage: ./scripts/generate-test-data.sh

set -e

echo "🔄 Generating test data for Social Rent App..."

# Запуск генерации тестовых данных через docker-compose
echo "👥 Generating 100 test users and 1000 listings..."
docker-compose run --rm test-data-generator python generate_test_data.py

echo "✅ Test data generation completed!"
echo "📊 Database now contains:"
echo "   - 100 test users with profiles"
echo "   - 1000 apartment listings in Moscow"
echo ""
echo "🚀 Ready for testing!"