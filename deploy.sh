#!/bin/bash

echo "🚀 Deploying CampusConnect to production..."

# Pull latest changes
echo "📥 Pulling latest code..."
git pull origin main

# Build containers
echo "🐳 Building Docker containers..."
docker-compose build

# Run database migrations
echo "📊 Running database migrations..."
docker-compose run --rm api alembic upgrade head

# Start services
echo "▶️  Starting services..."
docker-compose up -d

# Show status
echo "✅ Deployment complete!"
echo ""
echo "Services status:"
docker-compose ps

echo ""
echo "📋 View logs:"
echo "  docker-compose logs -f api"
echo ""
echo "🔍 Check health:"
echo "  curl http://localhost/health"
