#!/bin/bash

# Debbie's Travel Agent Assistant - Quick Start Script
# This script sets up and runs the application using Docker

echo "====================================="
echo "Debbie's Travel Agent Assistant"
echo "Quick Start Setup"
echo "====================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚠️  IMPORTANT: You need to edit .env and add your API credentials:"
    echo "   - Gmail API credentials"
    echo "   - Twilio credentials for SMS"
    echo "   - Email and phone for alerts"
    echo "   - Optional: OpenAI, Reddit API keys"
    echo ""
    read -p "Press Enter to open .env in your default editor (or edit it manually later)..."
    ${EDITOR:-nano} .env
fi

echo ""
echo "Starting services with Docker Compose..."
echo ""

# Stop any running containers
docker-compose down

# Build and start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

# Check if database is ready
echo "Checking database connection..."
docker-compose exec -T db pg_isready -U debbie_ta

if [ $? -eq 0 ]; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready. Please check logs with: docker-compose logs db"
    exit 1
fi

# Initialize database
echo ""
echo "Initializing database..."
docker-compose exec -T backend python -c "from app.database import init_db; init_db()"

echo ""
echo "====================================="
echo "✅ Setup Complete!"
echo "====================================="
echo ""
echo "The application is now running:"
echo ""
echo "📱 Frontend:        http://localhost:3000"
echo "🔧 Backend API:     http://localhost:8000"
echo "📚 API Docs:        http://localhost:8000/docs"
echo "🌸 Celery Monitor:  http://localhost:5555"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the application:"
echo "  docker-compose down"
echo ""
echo "⚠️  Next steps:"
echo "1. Make sure you've configured all API credentials in .env"
echo "2. Add clients via the API or frontend"
echo "3. Configure deal thresholds in Settings"
echo "4. The system will automatically check for deals every 12 hours"
echo ""
echo "Happy travels! ✈️"
