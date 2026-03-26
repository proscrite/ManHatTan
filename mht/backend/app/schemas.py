from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import datetime

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
    word_ul: Optional[str] = None        
    word_ll: Optional[str] = None
    lexeme_string: Optional[str] = None  
    p_recall: Optional[float] = None
    history_seen: Optional[int] = None
    history_correct: Optional[int] = None
    session_seen: Optional[int] = None
    session_correct: Optional[int] = None
    mdt_history: Optional[int] = None
    mdt_correct: Optional[int] = None
    mrt_history: Optional[int] = None
    mrt_correct: Optional[int] = None
    wdt_history: Optional[int] = None
    wdt_correct: Optional[int] = None
    wrt_history: Optional[int] = None
    wrt_correct: Optional[int] = None

class VocabularyResponse(VocabularyBase):
    id: str
    course_id: str
    p_recall: float
    history_seen: int
    history_correct: int
    next_review_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# REVIEW LOGS (EXERCISE PERFORMANCE)
# ==========================================
class ReviewCreate(BaseModel):
    vocab_id: str
    exercise_type: str
    user_answer: str
    speed: float

class ReviewResponse(BaseModel):
    id: str
    vocab_id: str
    exercise_type: str
    is_correct: bool
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