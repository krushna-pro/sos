"""
DATABASE.PY - Database Connection Setup
=======================================
This file sets up the connection to our database.
We use SQLAlchemy ORM (Object-Relational Mapping) which lets us 
work with database using Python objects instead of raw SQL queries.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


# =============================================================================
# DATABASE ENGINE
# =============================================================================
# The engine is the starting point for any SQLAlchemy application.
# It's the source of connections to the database.

# For SQLite, we need special settings
if settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}  # Needed for SQLite
    )
else:
    # For PostgreSQL/MySQL, no special args needed
    engine = create_engine(settings.DATABASE_URL)


# =============================================================================
# SESSION FACTORY
# =============================================================================
# Sessions are used to interact with the database.
# Each request gets its own session.

SessionLocal = sessionmaker(
    autocommit=False,  # Don't auto-commit, we control when to save
    autoflush=False,   # Don't auto-flush, we control when to sync
    bind=engine        # Connect to our engine
)


# =============================================================================
# BASE CLASS FOR MODELS
# =============================================================================
# All our database models (tables) will inherit from this Base class.
# It provides the mapping functionality.

Base = declarative_base()


# =============================================================================
# DATABASE DEPENDENCY
# =============================================================================
# This function is used with FastAPI's Depends() to get a database session.
# It ensures the session is properly closed after each request.

def get_db():
    """
    Generator function that provides database sessions.
    
    Usage in routes:
        @router.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    
    The 'yield' keyword makes this a generator.
    Code before yield runs before the request.
    Code after yield (in finally) runs after the request.
    """
    db = SessionLocal()
    try:
        yield db  # Provide the session to the route
    finally:
        db.close()  # Always close the session when done