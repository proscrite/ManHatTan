from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, Dict, Any, List
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

class CourseResponse(CourseBase):
    id: str
    user_id: str
    is_active: bool

    # This tells Pydantic to read the data directly from the SQLAlchemy ORM model
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