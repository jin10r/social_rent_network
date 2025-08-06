#!/bin/bash

# Script to download Python packages for offline installation
# Usage: ./scripts/prepare-offline-packages.sh

set -e

echo "🔄 Preparing offline Python packages..."

# Create offline packages directory
mkdir -p packages/python

# Download pip packages for offline installation
cd packages/python

echo "📦 Downloading backend dependencies..."
pip download -r ../../backend/requirements.txt --dest .

cd ../..

echo "✅ Python packages downloaded to packages/python/"
echo "💡 To install offline: pip install --no-index --find-links packages/python -r backend/requirements.txt"