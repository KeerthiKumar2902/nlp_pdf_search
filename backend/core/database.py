# backend/core/database.py
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import json

# Define the SQLite database URL.
# 'sqlite:///./sql_app.db' means the database will be a file named 'sql_app.db'
# in the current directory (which will be 'backend/').
DATABASE_URL = "sqlite:///./sql_app.db"

# Create the SQLAlchemy engine. The 'check_same_thread' is needed only for SQLite.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Each instance of SessionLocal will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base will be used by our ORM models to inherit from.
Base = declarative_base()

# --- Define our Document ORM Model ---
class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True, index=True)
    status = Column(String, default="processing")
    created_at = Column(DateTime, default=datetime.utcnow)

    # We will store the complex analysis results as a JSON string in a Text column.
    analysis_results = Column(Text, nullable=True)

def create_db_and_tables():
    # This function creates the database file and the 'documents' table
    # if they don't already exist.
    Base.metadata.create_all(bind=engine)
    print("Database and tables created successfully (if they didn't exist).")