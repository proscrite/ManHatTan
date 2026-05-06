import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# 1. Fetch the database URL from the settings configuration (will have to be injected by Docker or Azure)
# SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
SQLALCHEMY_DATABASE_URL = settings.database_url


## Outdated: Forced local SQLite 

# # 1. Get the absolute path of the directory where this database.py file lives
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# # 2. Force the database to ALWAYS be created inside the backend/app/ folder
# DB_PATH = os.path.join(BASE_DIR, "manhattan.db")
# SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()


# 2. Fallback to local SQLite if the environment variable is NOT set
if not SQLALCHEMY_DATABASE_URL:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, "manhattan.db")
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# 3. Dynamic Engine Configuration
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # SQLite requires check_same_thread
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Fix for newer SQLAlchemy versions which require 'postgresql://' instead of 'postgres://'
    if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # PostgreSQL does NOT accept check_same_thread
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()