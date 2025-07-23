#!/bin/bash
set -e

echo "🐳 Installing Docker on Ubuntu/Debian system..."
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Please don't run this script as root (without sudo)"
    echo "   Run as regular user: ./install-docker.sh"
    exit 1
fi

# Update package index
echo "📦 Updating package index..."
sudo apt-get update -qq

# Install prerequisites
echo "🔧 Installing prerequisites..."
sudo apt-get install -y -qq \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
echo "🔑 Adding Docker GPG key..."
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "📋 Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
echo "🔄 Updating package index with Docker repository..."
sudo apt-get update -qq

# Install Docker Engine
echo "🐳 Installing Docker Engine, CLI, and Compose..."
sudo apt-get install -y -qq \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin

# Add current user to docker group
echo "👤 Adding current user ($USER) to docker group..."
sudo usermod -aG docker $USER

# Start and enable Docker service
echo "🚀 Starting Docker service..."
sudo systemctl start docker
sudo systemctl enable docker

echo ""
echo "✅ Docker installation completed!"
echo ""
echo "⚠️  IMPORTANT: You need to log out and log back in (or run 'newgrp docker')"
echo "   for the group changes to take effect."
echo ""
echo "🧪 Test Docker installation:"
echo "   newgrp docker"
echo "   docker --version"
echo "   docker compose version"
echo ""
echo "🚀 Then you can run: ./start-local.sh" 