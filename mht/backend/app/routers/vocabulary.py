from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app import models, schemas

# Initialize the router for vocabulary-related endpoints
router = APIRouter(
    prefix="/api/v1/vocabulary",
    tags=["Vocabulary"]
)

# Dependency: This gets a database session for a single request, then closes it safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# The Route: When Flutter sends a GET request to /api/v1/vocabulary/{course_id}
@router.get("/{course_id}", response_model=List[schemas.VocabularyResponse])
def get_due_vocabulary(course_id: str, db: Session = Depends(get_db)):
    """
    Fetches all vocabulary words for a specific course.
    """
    # Query the SQLite database using SQLAlchemy
    words = db.query(models.UserVocabulary).filter(
        models.UserVocabulary.course_id == course_id
    ).all()
    
    if not words:
        raise HTTPException(status_code=404, detail="No words found for this course")
    
    # FastAPI automatically passes them through the Pydantic schemas.VocabularyResponse to format the JSON
    return words