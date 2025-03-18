# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# PostgreSQL Database URL
#DATABASE_URL = "postgresql://postgres:Rittik@8240@localhost/todoapp"
DATABASE_URL = "postgresql://postgres:1234@localhost/todoapp"
#DATABASE_URL = "postgresql://postgres:postgres@localhost/student"


# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL, 
    poolclass=NullPool  # Disable connection pooling for better resource management
)

# Create a SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a Base class for declarative models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
