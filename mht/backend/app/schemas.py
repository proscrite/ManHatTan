from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from enum import Enum

# ==========================================
# USERS
# ==========================================
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str

    class Config:
        from_attributes = True
        
# ==========================================
# USER COURSES
# ==========================================
class CourseBase(BaseModel):
    learning_language: str
    ui_language: str

class CourseCreate(CourseBase):
    pass  # Used when Flutter asks to create a new course

    cefr_level: int = Field(default=1, ge=1, le=6, description="1=A1, 2=A2, 3=B1, 4=B2, 5=C1, 6=C2")
    fluency_index: float = Field(default=0.0, ge=0.0, le=1.0, description="Intra-level fine score")

class CourseUpdate(BaseModel):
    is_active: Optional[bool] = None
    cefr_level: Optional[int] = Field(default=None, ge=1, le=6)
    fluency_index: Optional[float] = Field(default=None, ge=0.0, le=1.0)

class CourseResponse(CourseBase):
    id: str
    user_id: str
    is_active: bool
    cefr_level: int
    fluency_index: float

    model_config = ConfigDict(from_attributes=True)

# ==========================================
# VOCABULARY
# ==========================================
class VocabularyBase(BaseModel):
    word_ll: str
    word_ul: Optional[str] = None        
    lexeme_string: Optional[str] = None  
    source_type: Optional[str] = None    
    source_reference: Optional[str] = None
    context_sentence: Optional[str] = None

class VocabularyCreate(VocabularyBase):
    pass 

class VocabularyUpdate(BaseModel):
    # Allows partial updates to FSRS logic or Modality Stats
    word_ll: Optional[str] = None
    word_ul: Optional[str] = None
    lexeme_string: Optional[str] = None
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    context_sentence: Optional[str] = None
    fsrs_state: Optional[int] = None
    fsrs_difficulty: Optional[float] = None
    fsrs_stability: Optional[float] = None
    next_review_at: Optional[datetime] = None
    reps: Optional[int] = None
    lapses: Optional[int] = None
    modality_stats: Optional[Dict] = None

class VocabularyResponse(VocabularyBase):
    id: str
    course_id: str
    fsrs_state: int
    fsrs_difficulty: float
    fsrs_stability: float
    next_review_at: datetime
    reps: int
    lapses: int
    modality_stats: Dict
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# REVIEW LOGS (EXERCISE PERFORMANCE)
# ==========================================
class ReviewCreate(BaseModel):
    vocab_id: str
    exercise_type: str
    user_answer: str
    speed: float
    grade: int = Field(..., ge=1, le=4) # FSRS 1-4 scale

class ReviewResponse(BaseModel):
    id: str
    vocab_id: str
    exercise_type: str
    grade: int
    speed: float

    model_config = ConfigDict(from_attributes=True)

class MultipleChoiceResponse(BaseModel):
    vocab_id: str
    question_text: str       # The word to translate (e.g., English 'monster')
    options: List[str]       # The 4 shuffled options (e.g., Hebrew words)
    correct_answer: str      # The correct option (for frontend validation)

class WrittenExerciseResponse(BaseModel):
    vocab_id: str
    question_text: str
    correct_answer: str # We send this so the UI can show them what they missed!

# ==========================================
# LLM PROMPTING
# ==========================================

class LLMTaskType(str, Enum):
    CLOZE = "cloze"
    GRAMMAR_PILL = "grammar_pill"
    VOCAB_FACT = "vocab_fact"
    ETYMOLOGY = "etymology"
    WORD_ASSOCIATION = "word_association"

class LLMGenerationRequest(BaseModel):
    user_id: str
    task_type: LLMTaskType
    target_word: str
    target_lang: str = "Hebrew"
    native_lang: str = "English"
    context_data: Optional[Dict[str, Any]] = Field(default_factory=dict)

class LLMGenerationResponse(BaseModel):
    task_type: LLMTaskType
    content: Dict[str, Any]
    model_used: str

# --- Agent Tool Input Schemas ---

class FetchDueVocabInput(BaseModel):
    course_id: str = Field(
        ..., 
        description="The unique UUID of the user's active language course."
    )
    exclude_ids: List[str] = Field(
        default_factory=list, 
        description="UUIDs to exclude from the query (used for the session queue)."
    )

class ContextInput(BaseModel):
    target_word_ll: str = Field(
        ..., 
        description="The target vocabulary word in the learning language."
    )
    learning_language: str = Field(
        ..., 
        description="The full phonetic name of the learning language (e.g., 'Hebrew')."
    )
    limit: int = Field(
        default=3, 
        description="The maximum number of context sentences to retrieve from the vector database."
    )

# --- Agent Structured Output Schema ---

class ExerciseGenerationOutput(BaseModel):
    """
    Strict schema used by the Synthesizer Node to format the final exercise payload.
    """
    sentence_target: str = Field(
        ..., 
        description="The retrieved or generated context sentence in the target language, with the target word replaced by underscores (___)."
    )
    sentence_translated: str = Field(
        ..., 
        description="The translation of the sentence in the user's native language."
    )
    blank_word: str = Field(
        ..., 
        description="The correct target word that belongs in the blank."
    )
    options: List[str] = Field(
        ..., 
        description="A list containing the correct blank_word and 3 grammatically matching distractors."
    )

class GraderOutput(BaseModel):
    """
    Strict schema used by the Evaluator Node to grade retrieved vector context.
    """
    is_valid: bool = Field(
        description="True if the context is highly relevant and grammatically sound for the target word, False otherwise."
    )
    relevance_score: float = Field(
        description="A score between 0.0 and 1.0 indicating the quality and semantic alignment of the context."
    )

class TutorDecision(BaseModel):
    intervention_type: Literal["correction", "none"] = Field(
        description="Flag as 'correction' if a grammatical error occurred, otherwise 'none'."
    )
    tutor_critique_ll: Optional[str] = Field(
        default=None,
        description="The grammatical correction written entirely in the target learning language."
    )
    tutor_critique_ul: Optional[str] = Field(
        default=None,
        description="The exact translation of the grammatical correction in the user's native language."
    )

class ConversationalistResponse(BaseModel):
    message_ll: str = Field(
        description="The natural conversational reply in the target learning language."
    )
    message_ul: str = Field(
        description="The exact translation of the conversational reply in the user's native language."
    )

class ChatTurnRequest(BaseModel):
    user_message: str = Field(..., description="The user's latest message in the target language.")
    course_id: str = Field(..., description="The active course ID to retrieve user level and languages.")
    history_window: Optional[int] = Field(default=6, description="Number of recent turns to include in context.")

class ChatTurnResponse(BaseModel):
    conversationalist_message_ll: str
    conversationalist_message_ul: str
    tutor_critique_ll: Optional[str] = None
    tutor_critique_ul: Optional[str] = None