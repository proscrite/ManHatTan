# app/agent/tools.py
from langchain_core.tools import tool
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.schemas import FetchDueVocabInput, ContextInput
from app.services.exercise_service import get_next_exercise
from app.services.vector_service import vector_service

@tool("fetch_due_vocabulary", args_schema=FetchDueVocabInput)
def fetch_due_vocabulary(course_id: str, exclude_ids: List[str] = []) -> Dict[str, Any]:
    """
    Queries the Supabase PostgreSQL database to fetch the most urgent vocabulary word 
    due for Spaced Repetition (FSRS) review.
    """
    db: Session = SessionLocal()
    try:
        target = get_next_exercise(db=db, course_id=course_id, exclude_ids=exclude_ids)
        if not target:
            return {"status": "empty", "message": "No vocabulary is currently due."}
        
        return {
            "status": "success",
            "vocab_id": str(target.id),
            "target_word_ll": target.word_ll,
            "target_word_ul": target.word_ul,
            "fsrs_difficulty": target.fsrs_difficulty
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@tool("retrieve_milvus_context", args_schema=ContextInput)
def retrieve_milvus_context(target_word_ll: str, learning_language: str, limit: int = 3) -> Dict[str, Any]:
    """
    Queries the local Milvus vector database to retrieve semantically relevant 
    context sentences containing the target word.
    """
    try:
        hits = vector_service.search_context(
            target_word=target_word_ll, 
            language=learning_language, 
            limit=limit
        )
        
        if not hits:
            return {
                "status": "empty", 
                "message": f"No context sentences found in Milvus for '{target_word_ll}'."
            }

        return {
            "status": "success",
            "retrieved_sentences": hits
        }
    except Exception as e:
        return {"status": "error", "message": f"Milvus vector query failed: {str(e)}"}