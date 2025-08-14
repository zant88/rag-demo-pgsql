#!/bin/bash

# RAG Knowledge App - Docker Test Script
# This script tests if the Docker setup is working correctly

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_status "🧪 Testing RAG Knowledge App Docker Setup..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

# Check if services are running
print_status "📊 Checking service status..."
if docker compose ps | grep -q "Up"; then
    print_success "✅ Services are running!"
    docker compose ps
else
    print_warning "⚠️  Services are not running. Starting them..."
    docker compose up -d
    sleep 10
fi

# Test database connection
print_status "🗄️  Testing database connection..."
if docker compose exec -T postgres pg_isready -U apple -d rag_knowledge_db > /dev/null 2>&1; then
    print_success "✅ Database is ready!"
else
    print_error "❌ Database connection failed!"
    exit 1
fi

# Test backend health
print_status "🚀 Testing backend health..."
sleep 5  # Give backend time to start
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "✅ Backend is healthy!"
else
    print_warning "⚠️  Backend health check failed. Checking logs..."
    docker compose logs backend | tail -10
fi

# Test frontend
print_status "🌐 Testing frontend..."
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "✅ Frontend is accessible!"
else
    print_warning "⚠️  Frontend not accessible. Checking logs..."
    docker compose logs frontend | tail -10
fi

# Show final status
echo
print_status "📋 Final Status:"
print_status "   Frontend: http://localhost:3000"
print_status "   Backend API: http://localhost:8000"
print_status "   API Docs: http://localhost:8000/docs"
echo
print_status "🔍 To view detailed logs: docker compose logs -f [service_name]"
print_status "🛑 To stop services: docker compose down"

print_success "🎉 Docker setup test completed!"