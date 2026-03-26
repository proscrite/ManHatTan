from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal, get_db
from app import models, schemas

# Initialize the router for vocabulary-related endpoints
router = APIRouter(
    prefix="/api/v1/vocabulary",
    tags=["Vocabulary"]
)

# Dependency: This gets a database session for a single request, then closes it safely


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

@router.put("/{vocab_id}", response_model=schemas.VocabularyResponse)
def update_vocabulary(
    vocab_id: str, 
    payload: schemas.VocabularyUpdate, 
    db: Session = Depends(get_db)
):
    """
    Updates the text of a specific vocabulary word.
    """
    word = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == vocab_id).first()
    
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Update the fields
    word.word_ll = payload.word_ll
    word.word_ul = payload.word_ul
    
    db.commit()
    db.refresh(word)
    return word

@router.delete("/{vocab_id}")
def delete_vocabulary(vocab_id: str, db: Session = Depends(get_db)):
    """
    Permanently deletes a vocabulary word from the database.
    """
    word = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == vocab_id).first()
    
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    
    db.delete(word)
    db.commit()
    
    return {"message": "Vocabulary word deleted successfully"}