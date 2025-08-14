"""
Script to create all database tables from SQLAlchemy models.
"""

from app.core.database import engine, Base
from app.models import document, chunk, knowledge  # ensure all models are imported

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("All tables created.")
