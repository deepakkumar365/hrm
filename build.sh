#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🔧 Starting Render build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-render.txt

# Display environment info
echo "🌍 Environment: ${ENVIRONMENT:-not set}"
echo "🗄️  Database URL: ${PROD_DATABASE_URL:0:30}..." # Show first 30 chars only

# Run database migrations
echo "🔄 Running database migrations..."
export FLASK_SKIP_DB_INIT=1
flask db upgrade
unset FLASK_SKIP_DB_INIT

echo "✅ Build completed successfully!"