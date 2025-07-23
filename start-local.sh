#!/bin/bash
set -e

echo "🚀 Starting Document Processing Engine (Local Development)"
echo ""

# Function to detect docker compose command
detect_docker_compose() {
    # First check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed!"
        echo ""
        echo "📥 Install Docker using one of these methods:"
        echo "   • sudo apt install docker.io"
        echo "   • sudo snap install docker"
        echo "   • curl -fsSL https://get.docker.com | sh"
        echo ""
        echo "After installation, add your user to docker group:"
        echo "   sudo usermod -aG docker \$USER"
        echo "   newgrp docker"
        echo ""
        echo "Or run the install script: ./install-docker.sh"
        exit 1
    fi
    
    # Check for docker compose commands
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "❌ Docker Compose not found. Please install Docker Compose."
        echo "   Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi
}

DOCKER_COMPOSE_CMD=$(detect_docker_compose)
echo "📦 Using: $DOCKER_COMPOSE_CMD"
echo ""

# Check for port conflicts
echo "🔍 Checking for port conflicts..."
ports_in_use=()

if ss -tln | grep -q ":8000 "; then
    ports_in_use+=("8000 (API server)")
fi

if ss -tln | grep -q ":5432 "; then
    ports_in_use+=("5432 (PostgreSQL)")
fi

if ss -tln | grep -q ":9000 "; then
    ports_in_use+=("9000 (MinIO API)")
fi

if ss -tln | grep -q ":9001 "; then
    ports_in_use+=("9001 (MinIO Console)")
fi

if [ ${#ports_in_use[@]} -gt 0 ]; then
    echo "⚠️  The following ports are already in use:"
    for port in "${ports_in_use[@]}"; do
        echo "   • $port"
    done
    echo ""
    echo "Either stop the conflicting services or modify docker-compose.yml ports"
    echo "Press Enter to continue anyway or Ctrl+C to abort..."
    read
fi

echo "✅ Port check completed"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    echo ""
    echo "Please edit .env file and add your keys:"
    echo ""
    
    cat > .env << 'EOF'
# OpenAI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# API Authentication (change this to a secure random string)
API_KEY=your-secure-api-key-here

# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=docparser
DB_USER=docparser
DB_PASSWORD=docparser123

# Storage Configuration (S3-compatible - MinIO for local development)
S3_ENDPOINT_URL=http://minio:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin123
S3_BUCKET_NAME=documents
S3_REGION=us-east-1

# Local Development Flags
RUNNING_IN_LAMBDA=false
USE_LOCAL_STORAGE=true

# Docker Compose Configuration (these are used by docker-compose.yml, not the app)
APP_PORT=8000
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
EOF
    
    echo "✅ Created .env file"
    echo ""
    echo "🔧 Please edit .env file and update the following:"
    echo "   1. OPENAI_API_KEY=sk-your-actual-openai-api-key"
    echo "   2. API_KEY=your-secure-random-api-key (e.g., a UUID or long random string)"
    echo ""
    echo "Press Enter to continue after updating the .env file..."
    read
fi

# Check if keys are still default values
missing_keys=()

if grep -q "your-openai-api-key-here" .env; then
    missing_keys+=("OPENAI_API_KEY")
fi

if grep -q "your-secure-api-key-here" .env; then
    missing_keys+=("API_KEY")
fi

if [ ${#missing_keys[@]} -gt 0 ]; then
    echo "❌ Please update the following keys in .env file:"
    for key in "${missing_keys[@]}"; do
        if [ "$key" == "OPENAI_API_KEY" ]; then
            echo "   $key=sk-your-actual-openai-api-key"
        elif [ "$key" == "API_KEY" ]; then
            echo "   $key=your-secure-random-api-key"
        fi
    done
    echo ""
    exit 1
fi

echo "🐳 Starting Docker Compose services..."
echo ""

# Build and start services
$DOCKER_COMPOSE_CMD up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."

# Wait for services to be ready
max_attempts=12
attempt=0

while [ $attempt -lt $max_attempts ]; do
    # Check if API is responding
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        echo "✅ API server is ready"
        break
    fi
    echo "   Waiting for API... ($((attempt + 1))/$max_attempts)"
    sleep 5
    attempt=$((attempt + 1))
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ API server failed to start properly"
    echo "   Check logs with: $DOCKER_COMPOSE_CMD logs app"
    echo "   Check container status with: $DOCKER_COMPOSE_CMD ps"
    exit 1
fi

echo ""
echo "🎉 Document Processing Engine is running!"
echo ""
echo "📍 Access Points:"
echo "   • API Server:          http://localhost:8000"
echo "   • API Documentation:   http://localhost:8000/docs"
echo "   • MinIO Console:       http://localhost:9001"
echo "   • Database:            http://localhost:5432"
echo ""
echo "🔐 Credentials:"
echo "   • MinIO Console:       minioadmin / minioadmin123"
echo "   • Database:            docparser / docparser123"
echo ""
echo "📚 Commands:"
echo "   • View logs:           $DOCKER_COMPOSE_CMD logs -f"
echo "   • Stop services:       $DOCKER_COMPOSE_CMD down"
echo "   • Restart services:    $DOCKER_COMPOSE_CMD restart"
echo ""
echo "📄 Full documentation: README.local.md"
echo ""

# Test additional services
echo "🧪 Testing all services..."
echo -n "   • API Server:     "
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not responding"
fi

echo -n "   • MinIO Console:  "
if curl -s http://localhost:9001 > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not responding"
fi

echo -n "   • Database:       "
if $DOCKER_COMPOSE_CMD exec -T postgres pg_isready -U docparser > /dev/null 2>&1; then
    echo "✅ Ready"
else
    echo "❌ Not responding"
fi

echo ""
echo "🚀 Ready for development!" 