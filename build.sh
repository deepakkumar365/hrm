#!/usr/bin/env bash
# Build script for Render deployment

set -o errexit  # Exit on error

# Install dependencies
pip install -r requirements-render.txt

# Run database migrations
flask db upgrade