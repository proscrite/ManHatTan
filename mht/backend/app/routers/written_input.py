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

@router.get("/written", response_model=schemas.WrittenExerciseResponse)
def get_written_exercise(course_id: str, mode: str = "wrt", db: Session = Depends(get_db)):
    # Fetch the weakest word
    target = db.query(models.UserVocabulary).filter(
        models.UserVocabulary.course_id == course_id
    ).order_by(models.UserVocabulary.p_recall.asc()).first()

    if not target:
        raise HTTPException(status_code=404, detail="No vocabulary found for this course.")

    # Dynamic Assignment based on Modality (WIRTE vs WIDTE)
    if mode == "wdt":
        question_text = target.word_ll
        correct_answer = target.word_ul
    else: # wrt
        question_text = target.word_ul
        correct_answer = target.word_ll

    return schemas.WrittenExerciseResponse(
        vocab_id=target.id,
        question_text=question_text,
        correct_answer=correct_answer,
    )