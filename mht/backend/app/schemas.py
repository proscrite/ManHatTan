from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

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
    is_correct: bool
    speed: float
    # We don't need timestamp here; the backend generates it automatically

class ReviewResponse(ReviewCreate):
    id: str
    timestamp: datetime
    
    model_config = ConfigDict(from_attributes=True)