from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from rapidfuzz import utils, distance
from fsrs import FSRS, Card, Rating, State

from app.database import SessionLocal, get_db
from app import models, schemas

router = APIRouter(
    prefix="/api/v1/progress",
    tags=["Progress & Reviews"]
)

fsrs_scheduler = FSRS()

@router.post("/review", response_model=schemas.ReviewResponse)
def submit_exercise_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    vocab = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == review.vocab_id).first()
    if not vocab:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- DYNAMIC RAPIDFUZZ GRADING ---
    ex_type = review.exercise_type
    
    if ex_type not in vocab.modality_stats:
        vocab.modality_stats[ex_type] = {"seen": 0, "correct": 0}
        
    vocab.modality_stats[ex_type]["seen"] += 1

    if ex_type == "wdt":
        actual_correct = utils.default_process(vocab.word_ul) # Direct: Answer is English
    else: # wrt
        actual_correct = utils.default_process(vocab.word_ll) # Reverse: Answer is Hebrew

    provided_answer = utils.default_process(review.user_answer)
    score = distance.JaroWinkler.similarity(actual_correct, provided_answer)
    
    # Fuzzy threshold to FSRS grade mapping 
    # (Client can also provide 'review.grade', depending on the design,
    # but we refine it server-side for written answers)
    if score >= 0.95:
        computed_grade = 4  # Easy
    elif score >= 0.9:
        computed_grade = 3  # Good
    elif score >= 0.8:
        computed_grade = 2  # Hard
    else:
        computed_grade = 1  # Again
        
    # User subjective grade can override if it's strictly worse, or we just trust the computed
    final_grade = computed_grade

    # Update correct stats
    if final_grade >= 3:
        vocab.modality_stats[ex_type]["correct"] += 1

    safe_state = vocab.fsrs_state if vocab.fsrs_state is not None else State.New.value  
    safe_diff = vocab.fsrs_difficulty if vocab.fsrs_difficulty is not None else 0.0
    safe_stab = vocab.fsrs_stability if vocab.fsrs_stability is not None else 0.0
    safe_reps = vocab.reps if vocab.reps is not None else 0
    safe_lapses = vocab.lapses if vocab.lapses is not None else 0

    # --- FSRS INTEGRATION ---
    # 1. Instantiate a pristine, default card
    card = Card()
    
    # 2. Hydrate the card with your safe database state
    card.state = State(safe_state)
    card.difficulty = safe_diff
    card.stability = safe_stab
    card.reps = safe_reps
    card.lapses = safe_lapses

    if vocab.fsrs_last_review:
        card.last_review = vocab.fsrs_last_review.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    scheduling_cards = fsrs_scheduler.repeat(card, now)
    updated_card = scheduling_cards[Rating(final_grade)].card

    vocab.fsrs_state = updated_card.state.value
    vocab.fsrs_difficulty = updated_card.difficulty
    vocab.fsrs_stability = updated_card.stability
    vocab.reps = updated_card.reps
    vocab.lapses = updated_card.lapses
    vocab.fsrs_last_review = now.replace(tzinfo=None)
    vocab.next_review_at = updated_card.due.replace(tzinfo=None)

    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=ex_type,
        grade=final_grade,
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
        grade=new_review.grade,
        speed=new_review.speed,
        timestamp=new_review.timestamp
    )

@router.post("/review/multiple-choice", response_model=schemas.ReviewResponse)
def submit_mc_review(review: schemas.ReviewCreate, db: Session = Depends(get_db)):
    # Note: We will eventually add User Authentication here to ensure 
    # the user actually owns this vocab_id!
    vocab = db.query(models.UserVocabulary).filter(models.UserVocabulary.id == review.vocab_id).first()
    
    if not vocab:
        raise HTTPException(status_code=404, detail="Item not found")

    # --- DYNAMIC SECURE GRADING ---
    ex_type = review.exercise_type
    
    if ex_type not in vocab.modality_stats:
        vocab.modality_stats[ex_type] = {"seen": 0, "correct": 0}
        
    vocab.modality_stats[ex_type]["seen"] += 1

    # The server retains absolute authority over what is correct.
    if ex_type == "mdt":
        is_correct = (review.user_answer.strip() == vocab.word_ul.strip())
    else: # mrt (default/fallback)
        is_correct = (review.user_answer.strip() == vocab.word_ll.strip())
        
    if is_correct:
        vocab.modality_stats[ex_type]["correct"] += 1
        computed_grade = 3 # Default good for multiple-choice, unless specified by user. We can use review.grade
    else:
        computed_grade = 1

    # Allow subjective grade if the answer was correct, otherwise force fail
    final_grade = review.grade if is_correct and review.grade >= 2 else computed_grade

    safe_state = vocab.fsrs_state if vocab.fsrs_state is not None else State.New.value  
    safe_diff = vocab.fsrs_difficulty if vocab.fsrs_difficulty is not None else 0.0
    safe_stab = vocab.fsrs_stability if vocab.fsrs_stability is not None else 0.0
    safe_reps = vocab.reps if vocab.reps is not None else 0
    safe_lapses = vocab.lapses if vocab.lapses is not None else 0

    # --- FSRS INTEGRATION ---
    # 1. Instantiate a pristine, default card
    card = Card()
    
    # 2. Hydrate the card with your safe database state
    card.state = State(safe_state)
    card.difficulty = safe_diff
    card.stability = safe_stab
    card.reps = safe_reps
    card.lapses = safe_lapses


    if vocab.fsrs_last_review:
        card.last_review = vocab.fsrs_last_review.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    scheduling_cards = fsrs_scheduler.repeat(card, now)
    updated_card = scheduling_cards[Rating(final_grade)].card

    vocab.fsrs_state = updated_card.state.value
    vocab.fsrs_difficulty = updated_card.difficulty
    vocab.fsrs_stability = updated_card.stability
    vocab.reps = updated_card.reps
    vocab.lapses = updated_card.lapses
    vocab.fsrs_last_review = now.replace(tzinfo=None)
    vocab.next_review_at = updated_card.due.replace(tzinfo=None)

    new_review = models.ReviewLog(
        vocab_id=review.vocab_id,
        exercise_type=ex_type, # Records 'mrt' or 'mdt'
        grade=final_grade,
        speed=review.speed
    )
    db.add(new_review)

    # Save everything to the database
    db.commit()
    db.refresh(vocab)
    db.refresh(new_review) 

    # Return ALL the fields required by your schema
    return schemas.ReviewResponse(
        id=str(new_review.id),
        vocab_id=str(vocab.id),
        exercise_type=new_review.exercise_type,
        grade=new_review.grade,
        speed=new_review.speed,
        timestamp=new_review.timestamp
    )