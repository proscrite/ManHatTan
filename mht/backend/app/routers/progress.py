from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from rapidfuzz import utils, distance

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
    vocab = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == review.vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- THE GRADING ENGINE ---
    # 1. Clean both strings (lowercase, strip whitespace, remove punctuation)
    actual_correct = utils.default_process(vocab.word_ll)
    provided_answer = utils.default_process(review.user_answer)

    # 2. Calculate Similarity (0 to 100)
    # Using Jaro-Winkler distance which is great for short phrases/words
    score = distance.JaroWinkler.similarity(actual_correct, provided_answer)
    
    # 3. Decision Gate: 0.9 (90% match) allows for 1 tiny typo in a long word
    is_correct = score >= 0.9
    # ---------------------------

    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=review.exercise_type,
        is_correct=is_correct,
        speed=review.speed
    )
    db.add(new_review)

    # Update stats based on our backend decision
    vocab.history_seen += 1
    if is_correct:
        vocab.history_correct += 1
        vocab.p_recall = min(1.0, vocab.p_recall + 0.15)
    else:
        vocab.p_recall = max(0.0, vocab.p_recall - 0.25)

    db.commit()
    db.refresh(new_review)
    return new_review