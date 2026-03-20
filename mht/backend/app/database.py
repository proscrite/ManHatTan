import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Get the absolute path of the directory where this database.py file lives
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. Force the database to ALWAYS be created inside the backend/app/ folder
DB_PATH = os.path.join(BASE_DIR, "manhattan.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()