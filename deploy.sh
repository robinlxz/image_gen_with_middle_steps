#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Simple deployment script for ECS

echo "🚀 Starting Deployment..."

# 1. Update Code (if this is run via git pull)
# git pull

# 2. Setup Virtual Environment (if not exists)
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 3. Activate Environment
source venv/bin/activate

# 4. Install Dependencies
echo "📦 Installing dependencies..."
# Upgrade pip first to avoid some issues
pip install --upgrade pip
# Install with no cache to avoid corruption issues
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir gunicorn

# 5. Check Configuration
echo "🔍 Validating configuration..."
if [ ! -f ".env" ]; then
    echo "⚠️ .env file not found! Please create one from .env.example"
    exit 1
fi

# 6. Start Server (in background or managed by systemd usually, but here we run directly)
echo "🔥 Starting Gunicorn Server..."
# Run with gunicorn using our config file
# Note: In production, you might want to use 'nohup' or systemd
if pgrep gunicorn > /dev/null; then
    echo "⚠️ Gunicorn is already running. Restarting..."
    pkill gunicorn
    sleep 2
fi

gunicorn -c gunicorn_config.py app:app
