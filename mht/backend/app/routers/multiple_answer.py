from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
import random
from app.database import SessionLocal, get_db
from app import models, schemas
from app.models import UserVocabulary
from app.schemas import MultipleChoiceResponse

router = APIRouter(
    prefix="/api/v1/exercise",
    tags=["Exercises"]
)

@router.get("/multiple-choice", response_model=MultipleChoiceResponse)
def get_multiple_choice(course_id: str, mode: str = "mrt", db: Session = Depends(get_db)):
    
    # 1. Fetch the weakest word FOR THIS SPECIFIC COURSE
    target = db.query(UserVocabulary).filter(
        UserVocabulary.course_id == course_id, # Filter by course_id!
    ).order_by(UserVocabulary.p_recall.asc()).first()

    if not target:
        raise HTTPException(status_code=404, detail="No vocabulary found for this course/language.")

    # 2. Fetch 3 random distractor words from the SAME course
    distractors = db.query(UserVocabulary).filter(
        UserVocabulary.course_id == course_id,
        UserVocabulary.id != target.id
    ).order_by(func.random()).limit(3).all()

    # Fallback in case the user has fewer than 4 words in their database
    if len(distractors) < 3:
        raise HTTPException(status_code=400, detail="Not enough words in DB to generate distractors.")

    # 3. Dynamic Assignment based on Modality (MARTE vs MADTE)
    if mode == "mdt":
        # Direct: Prompt is Hebrew (LL), Options are English (UL)
        question_text = target.word_ll
        correct_answer = target.word_ul
        options = [target.word_ul] + [d.word_ul for d in distractors]
    else:
        # Reverse (mrt): Prompt is English (UL), Options are Hebrew (LL)
        question_text = target.word_ul
        correct_answer = target.word_ll
        options = [target.word_ll] + [d.word_ll for d in distractors]
    
    # 4. Shuffle the options
    random.shuffle(options)

    return MultipleChoiceResponse(
        vocab_id=target.id,
        question_text=question_text,
        options=options,
        correct_answer=correct_answer
    )