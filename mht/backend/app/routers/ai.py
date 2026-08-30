from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse

from litellm.exceptions import RateLimitError
import logging

from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage

from app.database import get_db
from app.models import UserCourse, User
from app.schemas import LLMGenerationRequest, LLMGenerationResponse, ChatTurnRequest, ChatTurnResponse
from app.security import get_current_user
from app.agent.mas_graph import mas_agent
from app.agent.mas_state import MASState
from app.services.llm_service import llm_service
from app.services.fluency_service import resolve_course_cefr
from app.services.vector_service import vector_service

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ai", tags=["AI Engine"])

@router.post("/generate", response_model=LLMGenerationResponse)
async def generate_ai_content(payload: LLMGenerationRequest):
    """
    Universal endpoint for dynamic language generation tasks:
    CLOZE, Grammar Pills, Vocab Facts, Etymology, and Word Associations.
    """
    try:
        # The service handles the LiteLLM routing, system prompt injection, and MLFlow tracing
        result = await llm_service.generate_content(payload)
        return result
    except RateLimitError as e:
        logger.warning(f"LLM Quota Exhausted: {str(e)}")
        # Return a clean 429 instead of a 500 crash
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="RATE_LIMIT"
        )
    except Exception as e:
        logger.error(f"LLM Generation Task Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate AI content.")

async def background_vector_cache(critique_ul: str, language: str):
    """Asynchronously embed and persist tutor critique into Zilliz Cloud."""
    try:
        await vector_service.insert_conversation_history(
            critique_ul=critique_ul,
            language=language
        )
    except Exception as e:
        print(f"[VectorService] Background ingestion error: {e}")

@router.post("/chat", response_model=ChatTurnResponse)
async def chat_turn(
    payload: ChatTurnRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Executes a Multi-Agent System (MAS) conversational turn:
    1. Tutor evaluates grammar and morphology.
    2. Conversationalist generates a target-language response.
    3. Asynchronously persists critiques to Zilliz in the background.
    """
    # 1. Fetch course metadata for linguistic guardrails
    course = db.query(UserCourse).filter(
        UserCourse.id == payload.course_id, 
        UserCourse.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course context not found.")

    cefr_label, _ = resolve_course_cefr(course.cefr_level or 1)

    # 2. Hydrate MAS State
    initial_state: MASState = {
        "messages": [HumanMessage(content=payload.user_message)],
        "fluency_index": getattr(course, "fluency_index", 0.5),
        "cefr_level": cefr_label,
        "target_lang": course.learning_language or "Hebrew",
        "native_lang": course.ui_language or "English",
        "due_vocab_id": None,
        "intervention_type": None,
        "tutor_critique_ll": None,
        "tutor_critique_ul": None,
        "conversationalist_message_ll": None,
        "conversationalist_message_ul": None
    }

    # 3. Invoke MAS Agent Graph
    try:
        final_state = await mas_agent.ainvoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MAS Agent Execution Failed: {str(e)}")

    # 4. Asynchronously persist critique to vector DB if generated
    if final_state.get("tutor_critique_ul"):
        background_tasks.add_task(
            background_vector_cache,
            user_id=str(current_user.id),
            critique_ul=final_state["tutor_critique_ul"],
            language=course.ui_language or "English"
        )

    # 5. Return decoupled dual-language payload
    return ChatTurnResponse(
        conversationalist_message_ll=final_state.get("conversationalist_message_ll", ""),
        conversationalist_message_ul=final_state.get("conversationalist_message_ul", ""),
        tutor_critique_ll=final_state.get("tutor_critique_ll"),
        tutor_critique_ul=final_state.get("tutor_critique_ul")
    )