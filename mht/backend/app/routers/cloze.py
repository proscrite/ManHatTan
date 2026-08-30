from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas import LLMGenerationRequest, LLMTaskType
from app.services.exercise_service import get_next_exercise
from app.services.llm_service import llm_service
from app.services.fluency_service import resolve_course_cefr
from app.agent.graph import tier1_agent, AgentState

router = APIRouter(
    prefix="/api/v1/exercise",
    tags=["Exercises"]
)
@router.get("/cloze")
async def get_cloze_exercise(
    course_id: str, 
    mode: str = "aimrt",
    exclude_ids: List[str] = Query(default=[]), 
    db: Session = Depends(get_db)
):
    # 1. Fetch target lexeme from PostgreSQL
    target = get_next_exercise(db=db, course_id=course_id, exclude_ids=exclude_ids)
    if not target:
        raise HTTPException(status_code=404, detail="No vocabulary found.")

    # 2. Extract discrete CEFR level from your newly migrated schema
    cefr_label, grammar_rules = resolve_course_cefr(target.course.cefr_level)

    # 3. Hydrate the initial LangGraph State
    initial_state: AgentState = {
        "vocab_id": str(target.id),
        "target_word": target.word_ll,
        "target_lang": target.course.learning_language,
        "native_lang": target.course.ui_language,
        "fsrs_difficulty": target.fsrs_difficulty,
        "cefr_level": cefr_label,
        "grammar_rules": grammar_rules,
        "retrieved_contexts": [], # Will be populated by the Graph's Retrieval Node
        "is_context_valid": False,
        "relevance_score": 0.0,
        "generated_payload": None
    }
    
    # 4. Execute the Evaluative RAG Graph
    try:
        final_state = await tier1_agent.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Execution Failed: {str(e)}")

    # 5. Return the structured Dart-compliant payload
    return {
        "vocab_id": target.id,
        "mode": mode,
        "exercise": final_state.get("generated_payload", {})
    }