"""Configuration settings for the application."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Server settings
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Project settings
    PROJECT_NAME: str = "Agentic RAG Knowledge App"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database settings
    DATABASE_URL: Optional[str] = None
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "rag_knowledge_db"
    DATABASE_USER: str = "apple"
    DATABASE_PASSWORD: str = "apple"

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Upload settings
    UPLOAD_FOLDER: str = "./uploads"
    MAX_FILE_SIZE: int = 50000000  # 50MB
    CHUNK_SIZE: int = 5000000      # 5MB
    
    # Document processing settings
    MAX_CHUNKS_PER_BATCH: int = 2000  # Maximum chunks to process in a single batch
    
    # Cohere API
    COHERE_API_KEY: str
    
    # Groq API
    GROQ_API_KEY: str
    
    # OCR settings
    TESSERACT_CMD: str = "/usr/bin/tesseract"
    
    # Neo4j settings (Optional)
    NEO4J_URI: Optional[str] = None
    NEO4J_USERNAME: Optional[str] = None
    NEO4J_PASSWORD: Optional[str] = None
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Create settings instance
settings = Settings()
