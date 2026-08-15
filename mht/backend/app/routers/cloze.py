from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import LLMGenerationRequest, LLMTaskType
from app.services.exercise_service import get_next_exercise
from app.services.llm_service import llm_service


router = APIRouter(
    prefix="/api/v1/exercise",
    tags=["Exercises"]
)
@router.get("/cloze")
async def get_cloze_exercise(
    course_id: str, 
    mode: str = "aimrt", # e.g., aimrt or aimdt
    exclude_ids: List[str] = Query(default=[]), 
    db: Session = Depends(get_db)
):
    # 1. Fetch the most urgent SRS word, honoring the session queue
    target = get_next_exercise(db=db, course_id=course_id, exclude_ids=exclude_ids)

    if not target:
        raise HTTPException(status_code=404, detail="No vocabulary found.")

    target_word = target.word_ll  # For Cloze exercises, we only use the target language word as the prompt

    # 3. Request Dynamic Sentence & Distractors from AI Engine
    llm_req = LLMGenerationRequest(
        target_word=target_word,
        target_lang=target.course.learning_language,
        native_lang=target.course.ui_language,
        task_type=LLMTaskType.CLOZE,
        user_id=course_id # Bypassing auth token for now as per MVP
    )
    
    llm_response = await llm_service.generate_content(llm_req)

    # 4. Return combined payload
    return {
        "vocab_id": target.id,
        "mode": mode,
        "exercise": llm_response.content
    }