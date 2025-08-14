# RAG Knowledge App - Docker Setup

This guide will help you run the RAG Knowledge App using Docker containers.

## Prerequisites

- Docker and Docker Compose installed on your system
- API keys for Cohere and Groq services

## Quick Start

### 1. Clone and Navigate to Project

```bash
cd /path/to/rag/doc-learning-2
```

### 2. Set Up Environment Variables

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
```

Edit the `.env` file and add your API keys:

```env
COHERE_API_KEY=your_actual_cohere_api_key
GROQ_API_KEY=your_actual_groq_api_key
```

### 3. Build and Start Services

```bash
# Build and start all services
docker compose up --build
```

Or run in detached mode:

```bash
docker compose up --build -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Services Overview

The Docker setup includes three main services:

### 🗄️ PostgreSQL Database (`postgres`)
- **Image**: `pgvector/pgvector:pg15` (includes vector extension)
- **Port**: 5432
- **Database**: `rag_knowledge_db`
- **Credentials**: `apple/apple`

### 🚀 FastAPI Backend (`backend`)
- **Port**: 8000
- **Features**: 
  - Document processing and chunking
  - Vector embeddings with Cohere
  - Semantic search
  - RESTful API

### 🌐 Next.js Frontend (`frontend`)
- **Port**: 3000
- **Features**:
  - Modern React UI with Tailwind CSS
  - File upload interface
  - Search functionality
  - Responsive design

## Development Commands

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

### Stop Services

```bash
# Stop all services
docker compose down

# Stop and remove volumes (⚠️ This will delete your data)
docker compose down -v
```

### Rebuild Services

```bash
# Rebuild specific service
docker compose build backend
docker compose build frontend

# Rebuild and restart
docker compose up --build backend
```

### Database Management

```bash
# Access PostgreSQL shell
docker compose exec postgres psql -U apple -d rag_knowledge_db

# View database tables
docker compose exec postgres psql -U apple -d rag_knowledge_db -c "\dt"
```

## Troubleshooting

### Common Issues

1. **Docker Not Running**
   ```bash
   # Error: Cannot connect to the Docker daemon
   # Solution: Start Docker Desktop and wait for it to fully initialize
   ```
   - **macOS**: Open Docker Desktop from Applications
   - **Windows**: Start Docker Desktop from Start Menu
   - **Linux**: `sudo systemctl start docker`

2. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :3000  # or :8000, :5432
   
   # Kill the process or change ports in docker-compose.yml
   ```

3. **Frontend Build Issues (Missing public directory)**
   ```bash
   # If you get "public: not found" error
   # This is fixed in the Dockerfile, but if issues persist:
   mkdir -p frontend/public
   docker compose build --no-cache frontend
   ```

4. **Database Connection Issues**
   ```bash
   # Check if PostgreSQL is healthy
   docker-compose ps
   
   # View database logs
   docker-compose logs postgres
   ```

5. **API Keys Not Working**
   - Ensure your `.env` file is in the project root
   - Verify API keys are valid and have sufficient credits
   - Restart services after updating environment variables

6. **Build Cache Issues**
   ```bash
   # Clear Docker build cache and rebuild
   docker compose build --no-cache
   docker system prune -f
   ```

### Health Checks

All services include health checks:

```bash
# Check service health
docker compose ps

# Manual health check
curl http://localhost:8000/health  # Backend
curl http://localhost:3000         # Frontend
```

### Performance Optimization

1. **Increase Docker Resources**
   - Allocate more RAM and CPU to Docker
   - Recommended: 4GB RAM, 2 CPU cores

2. **Volume Mounting for Development**
   ```yaml
   # Add to docker-compose.yml for live reloading
   volumes:
     - ./backend:/app
     - ./frontend:/app
   ```

## Production Deployment

For production deployment:

1. **Update Environment Variables**
   ```env
   DEBUG=false
   NODE_ENV=production
   ```

2. **Use External Database**
   ```env
   DATABASE_URL=postgresql://user:pass@external-db:5432/dbname
   ```

3. **Configure Reverse Proxy**
   - Use Nginx or Traefik for SSL termination
   - Set up proper domain routing

4. **Security Considerations**
   - Remove default credentials
   - Use secrets management
   - Enable HTTPS
   - Restrict CORS origins

## Data Persistence

Database data is persisted in a Docker volume:

```bash
# List volumes
docker volume ls

# Backup database
docker compose exec postgres pg_dump -U apple rag_knowledge_db > backup.sql

# Restore database
docker compose exec -T postgres psql -U apple rag_knowledge_db < backup.sql
```

## Support

If you encounter issues:

1. Check the logs: `docker compose logs -f`
2. Verify all environment variables are set
3. Ensure Docker has sufficient resources
4. Try rebuilding with `--no-cache` flag

For more detailed API documentation, visit http://localhost:8000/docs after starting the services.