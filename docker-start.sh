#!/bin/bash

# RAG Knowledge App - Docker Startup Script
# This script helps you start the application using Docker

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

print_status "🚀 Starting RAG Knowledge App with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker Desktop and try again."
    echo
    print_status "📋 To start Docker:"
    print_status "   • On macOS: Open Docker Desktop application from Applications"
    print_status "   • On Linux: sudo systemctl start docker"
    print_status "   • On Windows: Start Docker Desktop from Start Menu"
    echo
    print_status "💡 After starting Docker, wait a moment for it to fully initialize, then run this script again."
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_warning ".env file not found. Creating from template..."
    cp .env.example .env
    print_warning "⚠️  Please edit .env file and add your API keys:"
    print_warning "   - COHERE_API_KEY"
    print_warning "   - GROQ_API_KEY"
    print_status "You can continue without API keys for testing, but some features won't work."
fi

# Check if API keys are set
if grep -q "your_.*_api_key_here" .env; then
    print_warning "⚠️  API keys not configured in .env file."
    print_warning "Some features may not work without proper API keys."
fi

print_status "🔧 Building Docker images..."
if docker compose build; then
    print_success "✅ Docker images built successfully!"
    print_status "📊 Note: Database migrations will be automatically run during container startup."
else
    print_error "❌ Failed to build Docker images. Check the logs above."
    exit 1
fi

print_status "🚀 Starting services..."
if docker compose up -d; then
    print_success "✅ Services started successfully!"
    echo
    print_status "🌐 Application URLs:"
    print_status "   Frontend: http://localhost:3000"
    print_status "   Backend API: http://localhost:8000"
    print_status "   API Docs: http://localhost:8000/docs"
    echo
    print_status "📊 To view logs: docker compose logs -f"
    print_status "🛑 To stop: docker compose down"
    echo
    print_status "⏳ Services are starting up... Please wait a moment before accessing the URLs."
else
    print_error "❌ Failed to start services. Check the logs above."
    exit 1
fi