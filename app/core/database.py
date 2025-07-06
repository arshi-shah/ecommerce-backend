from sqlalchemy import create_engine #Used to connect to DB
from sqlalchemy.orm import sessionmaker, declarative_base #ORM utilities for sessions and models
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL) #Create SQLAlchemy engine using PostgreSQL URL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) #Create a DB session factory
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()