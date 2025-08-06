#!/bin/bash

# Script to download Node.js packages for offline installation  
# Usage: ./scripts/prepare-offline-node-packages.sh

set -e

echo "🔄 Preparing offline Node.js packages..."

# Create offline packages directory
mkdir -p packages/node

cd frontend

echo "📦 Downloading frontend dependencies..."

# Create offline cache using yarn
yarn install --prefer-offline
yarn cache dir > ../packages/node/yarn-cache-location.txt

# Copy yarn cache for offline usage
YARN_CACHE_DIR=$(yarn cache dir)
cp -r "$YARN_CACHE_DIR" ../packages/node/yarn-cache/

# Create package tarball
yarn pack --filename ../packages/node/frontend-packages.tgz

cd ..

echo "✅ Node.js packages prepared in packages/node/"
echo "💡 To install offline: yarn install --offline --cache-folder packages/node/yarn-cache"