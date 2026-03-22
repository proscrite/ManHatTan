from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from rapidfuzz import utils, distance

from app.database import SessionLocal, get_db
from app import models, schemas

router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress & Reviews"]
)

@router.post("/review", response_model=schemas.ReviewResponse)
def submit_exercise_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    vocab = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == review.vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- DYNAMIC RAPIDFUZZ GRADING ---
    if review.exercise_type == "wdt":
        actual_correct = utils.default_process(vocab.word_ul) # Direct: Answer is English
        vocab.wdt_history += 1
    else: # wrt
        actual_correct = utils.default_process(vocab.word_ll) # Reverse: Answer is Hebrew
        vocab.wrt_history += 1

    provided_answer = utils.default_process(review.user_answer)
    score = distance.JaroWinkler.similarity(actual_correct, provided_answer)
    is_correct = score >= 0.9

    # Update correct stats
    if is_correct:
        if review.exercise_type == "wdt":
            vocab.wdt_correct += 1
        else:
            vocab.wrt_correct += 1
        vocab.history_correct += 1

    vocab.history_seen += 1
    if vocab.history_seen > 0:
        vocab.p_recall = round(vocab.history_correct / vocab.history_seen, 3)

    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=review.exercise_type,
        is_correct=is_correct,
        speed=review.speed
    )
    db.add(new_review)
    db.commit()
    db.refresh(vocab)
    db.refresh(new_review)

    return schemas.ReviewResponse(
        id=str(new_review.id),
        vocab_id=str(vocab.id),
        exercise_type=new_review.exercise_type,
        is_correct=new_review.is_correct,
        speed=new_review.speed,
        new_p_recall=vocab.p_recall
    )

@router.post("/review/multiple-choice", response_model=schemas.ReviewResponse)
def submit_mc_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Note: We will eventually add User Authentication here to ensure 
    # the user actually owns this vocab_id!
    vocab = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == review.vocab_id).first()
    
    if not vocab:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- DYNAMIC SECURE GRADING ---
    # The server retains absolute authority over what is correct.
    if review.exercise_type == "mdt":
        is_correct = (review.user_answer.strip() == vocab.word_ul.strip())
        vocab.mdt_history += 1
        if is_correct:
            vocab.mdt_correct += 1
    else: # mrt (default/fallback)
        is_correct = (review.user_answer.strip() == vocab.word_ll.strip())
        vocab.mrt_history += 1
        if is_correct:
            vocab.mrt_correct += 1

    # --- GLOBAL STATS & P_RECALL ---
    vocab.history_seen += 1
    if is_correct:
        vocab.history_correct += 1
        
    if vocab.history_seen > 0:
        vocab.p_recall = round(vocab.history_correct / vocab.history_seen, 3)

    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=review.exercise_type, # Records 'mrt' or 'mdt'
        is_correct=is_correct,
        speed=review.speed
    )
    db.add(new_review)

    # Save everything to the database
    db.commit()
    db.refresh(vocab)
    db.refresh(new_review) # This will no longer throw a NameError!

    # Return ALL the fields required by your schema
    return schemas.ReviewResponse(
        id=str(new_review.id),
        vocab_id=str(vocab.id),
        exercise_type=new_review.exercise_type,
        is_correct=new_review.is_correct,
        speed=new_review.speed,
        new_p_recall=vocab.p_recall 
    )