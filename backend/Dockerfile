FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libpq-dev \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Alembic for database migrations
RUN pip install alembic

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY . .

# Copy Alembic configuration and migrations from project root
COPY ../alembic.ini ./
COPY ../migrations ./migrations/

# Create uploads directory
RUN mkdir -p uploads

# Expose port
EXPOSE 8000

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting RAG Knowledge App Backend..."\n\
echo "🔧 Initializing database..."\n\
python init_db.py\n\
echo "🌟 Starting FastAPI server..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh && \
    chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]