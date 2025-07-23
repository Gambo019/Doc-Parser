#!/bin/bash
set -e

echo "🧹 Document Processing Engine - Cleanup Script"
echo ""

# Function to detect docker compose command
detect_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "❌ Docker Compose not found."
        exit 1
    fi
}

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Nothing to clean up."
    exit 0
fi

DOCKER_COMPOSE_CMD=$(detect_docker_compose)
echo "📦 Using: $DOCKER_COMPOSE_CMD"
echo ""

# Step 1: Stop and remove containers
echo "🛑 Step 1: Stopping and removing containers..."
if $DOCKER_COMPOSE_CMD ps -q > /dev/null 2>&1; then
    $DOCKER_COMPOSE_CMD down
    echo "   ✅ Containers stopped and removed"
else
    echo "   ℹ️  No running containers found"
fi

# Step 2: Remove volumes (with confirmation)
echo ""
echo "🗑️  Step 2: Removing persistent data volumes..."
echo "   ⚠️  This will delete all database and MinIO data!"
echo -n "   Continue? (y/N): "
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    $DOCKER_COMPOSE_CMD down -v
    echo "   ✅ Volumes removed"
else
    echo "   ℹ️  Volumes kept (data preserved)"
fi

# Step 3: Remove Docker images
echo ""
echo "🗑️  Step 3: Removing Docker images..."
echo -n "   Remove built application images? (y/N): "
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    # Remove the custom built image
    if docker images -q doc-parser-app > /dev/null 2>&1; then
        docker rmi doc-parser-app 2>/dev/null || true
        echo "   ✅ Application image removed"
    fi
    
    # Remove downloaded images
    images=("minio/minio:latest" "minio/mc:latest" "postgres:15-alpine")
    for image in "${images[@]}"; do
        if docker images -q "$image" > /dev/null 2>&1; then
            docker rmi "$image" 2>/dev/null || true
            echo "   ✅ Removed: $image"
        fi
    done
else
    echo "   ℹ️  Docker images kept"
fi

# Step 4: Clean Docker system
echo ""
echo "🧽 Step 4: Cleaning Docker system..."
echo -n "   Remove unused Docker resources? (y/N): "
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    docker system prune -f
    echo "   ✅ Docker system cleaned"
else
    echo "   ℹ️  Docker system not cleaned"
fi

# Step 5: Remove configuration files
echo ""
echo "🗑️  Step 5: Removing configuration files..."
echo -n "   Remove .env file? (y/N): "
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -f ".env" ]; then
        rm .env
        echo "   ✅ .env file removed"
    else
        echo "   ℹ️  .env file not found"
    fi
else
    echo "   ℹ️  .env file kept"
fi

# Step 6: Remove networks
echo ""
echo "🌐 Step 6: Cleaning up networks..."
if docker network ls | grep -q "doc-parser-network"; then
    docker network rm doc-parser-network 2>/dev/null || true
    echo "   ✅ doc-parser-network removed"
else
    echo "   ℹ️  Network already removed"
fi

# Final verification
echo ""
echo "🔍 Verification:"
echo -n "   • Containers: "
if [ "$(docker ps -a -q -f name=doc-parser)" ]; then
    echo "❌ Some containers still exist"
else
    echo "✅ All cleaned up"
fi

echo -n "   • Volumes: "
if [ "$(docker volume ls -q -f name=doc-parser)" ]; then
    echo "ℹ️  Some volumes still exist (preserved by choice)"
else
    echo "✅ All cleaned up"
fi

echo -n "   • Images: "
if docker images -q doc-parser-app > /dev/null 2>&1; then
    echo "ℹ️  Application image still exists (preserved by choice)"
else
    echo "✅ Application images cleaned up"
fi

echo -n "   • Networks: "
if docker network ls | grep -q "doc-parser-network"; then
    echo "❌ Network still exists"
else
    echo "✅ Network cleaned up"
fi

echo ""
echo "🎉 Cleanup completed!"
echo ""
echo "📋 What was cleaned:"
echo "   • All running containers stopped"
echo "   • Container definitions removed"
echo "   • Networks cleaned up"
echo "   • Optional: Data volumes, images, .env file"
echo ""
echo "🚀 To redeploy from scratch:"
echo "   ./start-local.sh" 