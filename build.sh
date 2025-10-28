#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

echo "🔧 Starting Render build process..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements-render.txt

# Display environment info
echo "🌍 Environment: ${ENVIRONMENT:-not set}"
echo "🗄️  Prod DB URL preview: ${PROD_DATABASE_URL:0:30}..." # Show first 30 chars only

# Ensure DATABASE_URL is set for Flask/Alembic tools
if [ "${ENVIRONMENT}" = "production" ]; then
	if [ -z "${PROD_DATABASE_URL}" ]; then
		echo "[ERROR] PROD_DATABASE_URL is not set but ENVIRONMENT=production"
		exit 2
	fi
	export DATABASE_URL="${PROD_DATABASE_URL}"
else
	# Prefer DEV_DATABASE_URL when present, otherwise fall back to existing DATABASE_URL
	export DATABASE_URL="${DEV_DATABASE_URL:-${DATABASE_URL}}"
fi
echo "🔎 Using DATABASE_URL: ${DATABASE_URL:0:30}..."

# Run database migrations during build
# This ensures tables are created before app starts
# Note: If AUTO_MIGRATE_ON_STARTUP=false, the app will also check and run migrations on startup
echo "🔄 Running database migrations during build..."
export FLASK_SKIP_DB_INIT=1
flask db upgrade
unset FLASK_SKIP_DB_INIT

# Verify schema after migrations
echo "🧾 Verifying database schema..."
if python verify_db.py; then
	echo "✅ Schema verification passed."
else
	echo "❌ Schema verification failed. Aborting build."
	exit 1
fi

echo "✅ Build completed successfully!"
echo "📝 Note: If AUTO_MIGRATE_ON_STARTUP is not set, app will auto-check tables on startup"