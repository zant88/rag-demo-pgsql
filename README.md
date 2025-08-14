# Agentic RAG-Based Knowledge App

A Retrieval-Augmented Generation (RAG) knowledge-based application with smart document upload and semantic search capabilities.

## Features

- **Document Upload & Chunking**: Resumable uploads with chunking for large files (PDF, DOCX, etc.)
- **Smart Text Extraction**: OCR with Tesseract for image-based documents
- **Advanced Text Cleaning**: Automatic removal of watermarks, headers/footers, page numbers
- **Indonesian Language Processing**: Specialized chunking with spacy-id or stanza
- **Semantic Search**: Vector similarity search with pgvector/PostgreSQL
- **Graph Database Integration**: Optional Neo4j for entity relationships and reasoning
- **Manual Knowledge Input**: Structured form interface for manual knowledge entry
- **Metadata-aware Responses**: Source tracing in all chatbot responses
- **Agentic Behavior**: Multi-hop reasoning across related concepts

## Tech Stack

- **Frontend**: React + Tailwind CSS
- **Backend**: FastAPI + Langchain + Cohere
- **Vector Database**: PostgreSQL with pgvector
- **Graph Database**: Neo4j (optional)
- **OCR**: pytesseract
- **NLP**: spaCy with Indonesian model (spacy-id) or stanza

## Project Structure

```
doc-learning-2/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Configuration and utilities
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API service calls
│   │   └── styles/         # CSS/Tailwind styles
│   ├── package.json        # Node.js dependencies
│   └── tailwind.config.js  # Tailwind configuration
└── README.md              # This file
```

## Quick Start

### Using the Startup Script (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   cd doc-learning-2
   ```

2. **Create virtual environment (if not exists):**
   ```bash
   python -m venv venv
   ```

3. **Start both servers:**
   ```bash
   ./start_servers.sh
   ```

   This script will:
   - Activate the virtual environment
   - Install backend dependencies
   - Install frontend dependencies (if needed)
   - Start the backend server on http://localhost:8000
   - Start the frontend server on http://localhost:3000
   - Display helpful URLs and status information

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

5. **Stop servers:**
   Press `Ctrl+C` to stop both servers gracefully.

### Manual Setup

If you prefer to start servers manually:

1. **Backend:**
   ```bash
   source venv/bin/activate
   pip install -r backend/requirements.txt
   cd backend
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Frontend (in another terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## VPS/Production Deployment

### Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+ (with pgvector extension)
- Nginx (for reverse proxy)
- PM2 (for process management)
- SSL certificate (Let's Encrypt recommended)

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nodejs npm postgresql postgresql-contrib nginx git

# Install PM2 globally
sudo npm install -g pm2

# Install PostgreSQL pgvector extension
sudo apt install -y postgresql-server-dev-all
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE rag_knowledge_db;
CREATE USER rag_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE rag_knowledge_db TO rag_user;

# Enable pgvector extension
\c rag_knowledge_db
CREATE EXTENSION vector;

# Exit PostgreSQL
\q
```

### 3. Project Deployment

```bash
# Clone the repository
git clone <your-repo-url> /var/www/doc-learning-2
cd /var/www/doc-learning-2

# Set proper permissions
sudo chown -R $USER:$USER /var/www/doc-learning-2
chmod +x start_servers.sh
```

### 4. Backend Configuration

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Create production environment file
cp .env.example .env
```

**Edit `.env` file with production settings:**
```bash
# Database Configuration
DATABASE_URL=postgresql://rag_user:your_secure_password@localhost/rag_knowledge_db

# API Keys
COHERE_API_KEY=your_cohere_api_key

# Security
SECRET_KEY=your_very_secure_secret_key_here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# File Upload Settings
UPLOAD_FOLDER=/var/www/doc-learning-2/backend/uploads
MAX_FILE_SIZE=50000000
CHUNK_SIZE=5000000
MAX_CHUNKS_PER_BATCH=2000

# Production Settings
ENVIRONMENT=production
DEBUG=false
```

### 5. Database Migration with Alembic

```bash
# Ensure you're in the backend directory with activated venv
cd /var/www/doc-learning-2/backend
source ../venv/bin/activate

# Initialize Alembic (if not already done)
# alembic init migrations

# Generate migration for current models
alembic revision --autogenerate -m "Initial migration"

# Apply migrations to database
alembic upgrade head

# Verify migration status
alembic current
alembic history
```

**For future schema changes:**
```bash
# After modifying models, generate new migration
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in migrations/versions/
# Apply the migration
alembic upgrade head

# Rollback if needed (to previous revision)
alembic downgrade -1
```

### 6. Frontend Build

```bash
cd /var/www/doc-learning-2/frontend

# Install dependencies
npm install

# Build for production
npm run build

# Test the build
npm start
```

### 7. Process Management with PM2

**Create PM2 ecosystem file:**
```bash
# Create ecosystem.config.js in project root
cat > /var/www/doc-learning-2/ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'rag-backend',
      cwd: '/var/www/doc-learning-2/backend',
      script: '../venv/bin/uvicorn',
      args: 'app.main:app --host 0.0.0.0 --port 8000',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'production'
      },
      error_file: '/var/log/pm2/rag-backend-error.log',
      out_file: '/var/log/pm2/rag-backend-out.log',
      log_file: '/var/log/pm2/rag-backend.log'
    },
    {
      name: 'rag-frontend',
      cwd: '/var/www/doc-learning-2/frontend',
      script: 'npm',
      args: 'start',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: '/var/log/pm2/rag-frontend-error.log',
      out_file: '/var/log/pm2/rag-frontend-out.log',
      log_file: '/var/log/pm2/rag-frontend.log'
    }
  ]
};
EOF
```

**Start applications with PM2:**
```bash
# Create log directory
sudo mkdir -p /var/log/pm2
sudo chown $USER:$USER /var/log/pm2

# Start applications
cd /var/www/doc-learning-2
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $USER --hp $HOME

# Monitor applications
pm2 status
pm2 logs
pm2 monit
```

### 8. Nginx Configuration

**Create Nginx configuration:**
```bash
sudo nano /etc/nginx/sites-available/rag-app
```

**Add the following configuration:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Handle large file uploads
        client_max_body_size 50M;
        proxy_request_buffering off;
    }
    
    # Static files and uploads
    location /uploads {
        alias /var/www/doc-learning-2/backend/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**Enable the site:**
```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/rag-app /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 9. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run
```

### 10. Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Check status
sudo ufw status
```

### 11. Monitoring and Maintenance

**System monitoring:**
```bash
# Check application status
pm2 status
pm2 logs --lines 50

# Check system resources
htop
df -h
free -h

# Check Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Check database status
sudo systemctl status postgresql
```

**Database backup:**
```bash
# Create backup script
cat > /home/$USER/backup_db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/home/$USER/backups"
DATE=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# Backup database
pg_dump -h localhost -U rag_user -d rag_knowledge_db > $BACKUP_DIR/rag_db_$DATE.sql

# Keep only last 7 days of backups
find $BACKUP_DIR -name "rag_db_*.sql" -mtime +7 -delete

echo "Database backup completed: rag_db_$DATE.sql"
EOF

chmod +x /home/$USER/backup_db.sh

# Add to crontab for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /home/$USER/backup_db.sh") | crontab -
```

**Update deployment:**
```bash
# Pull latest changes
cd /var/www/doc-learning-2
git pull origin main

# Update backend
source venv/bin/activate
cd backend
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Update frontend
cd ../frontend
npm install
npm run build

# Restart applications
pm2 restart all

# Check status
pm2 status
```

### Troubleshooting

**Common issues:**

1. **Database connection errors:**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check database connectivity
   psql -h localhost -U rag_user -d rag_knowledge_db
   ```

2. **Permission errors:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER /var/www/doc-learning-2
   chmod -R 755 /var/www/doc-learning-2
   ```

3. **PM2 process issues:**
   ```bash
   # Restart specific app
   pm2 restart rag-backend
   pm2 restart rag-frontend
   
   # View detailed logs
   pm2 logs rag-backend --lines 100
   ```

4. **Nginx issues:**
   ```bash
   # Test configuration
   sudo nginx -t
   
   # Reload configuration
   sudo systemctl reload nginx
   ```

### Performance Optimization

1. **Database optimization:**
   ```sql
   -- Create indexes for better performance
   CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
   CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON chunks USING ivfflat (embedding vector_cosine_ops);
   ```

2. **Enable Gzip compression in Nginx:**
   ```nginx
   # Add to server block
   gzip on;
   gzip_vary on;
   gzip_min_length 1024;
   gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
   ```

3. **PM2 cluster mode for backend:**
   ```javascript
   // In ecosystem.config.js, change backend config:
   {
     name: 'rag-backend',
     instances: 'max', // Use all CPU cores
     exec_mode: 'cluster'
   }
   ```
