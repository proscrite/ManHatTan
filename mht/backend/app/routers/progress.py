from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import SessionLocal
from app import models, schemas

router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress & Reviews"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/review", response_model=schemas.ReviewResponse)
def submit_exercise_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    """
    Submits a review for a specific vocabulary word, logs the event, 
    and updates the user's recall metrics.
    """
    # 1. Verify the vocabulary word exists in the database
    vocab = db.query(models.UserVocabulary).filter(
        models.UserVocabulary.id == review.vocab_id
    ).first()
    
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary item not found")

    # 2. Append the event to the Review Logs (for future ML training)
    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=review.exercise_type,
        is_correct=review.is_correct,
        speed=review.speed
    )
    db.add(new_review)

    # 3. Update the aggregate metrics on the Vocabulary table
    vocab.history_seen += 1
    vocab.session_seen += 1
    
    if review.is_correct:
        vocab.history_correct += 1
        vocab.session_correct += 1
        # Temporary naive math: Increase recall probability
        vocab.p_recall = min(1.0, vocab.p_recall + 0.1) 
    else:
        # Temporary naive math: Decrease recall probability
        vocab.p_recall = max(0.0, vocab.p_recall - 0.2)

    # 4. Commit the transaction to SQLite
    db.commit()
    db.refresh(new_review)

    # Returning this passes it through schemas.ReviewResponse
    return new_review