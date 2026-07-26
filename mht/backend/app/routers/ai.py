from fastapi import APIRouter, HTTPException
from app.schemas import LLMGenerationRequest, LLMGenerationResponse
from app.services.llm_service import llm_service
import logging

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
    except Exception as e:
        logger.error(f"LLM Generation Task Failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate AI content.")