import uuid
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime, JSON, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from app.database import Base
import datetime
from fsrs import State

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True)

    hashed_password = Column(String)

    # Relationships allow you to easily fetch a user's courses
    courses = relationship("UserCourse", back_populates="owner")

class UserCourse(Base):
    __tablename__ = "user_courses"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    learning_language = Column(String, index=True) # e.g., 'de', 'iw'
    ui_language = Column(String) # e.g., 'en'
    is_active = Column(Boolean, default=True)
    cefr_level = Column(Integer, nullable=True) # Optional CEFR level for the course: values 1-6 (A1-C2)
    fluency_index = Column(Float, nullable=True) # Intra-level progression metric (0.0-1.0) 

    owner = relationship("User", back_populates="courses")
    vocabulary = relationship("UserVocabulary", back_populates="course")

class UserVocabulary(Base):
    __tablename__ = "user_vocabulary"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    course_id = Column(String(36), ForeignKey("user_courses.id"))
    
    word_ll = Column(String, index=True)
    word_ul = Column(String)
    lexeme_string = Column(String)
    
    source_type = Column(String) # 'kindle', 'gtranslate', etc.
    source_reference = Column(String) 
    context_sentence = Column(String, nullable=True)
    
    # Metrics
    # FSRS Core Metrics
    fsrs_state = Column(Integer, server_default=str(State.New.value)) # 1=New, 2=Learning, 3=Review, 4=Relearning
    
    fsrs_difficulty = Column(Float, server_default="0.0")
    fsrs_stability = Column(Float, server_default="0.0")
    fsrs_last_review = Column(DateTime, nullable=True)
    next_review_at = Column(DateTime, server_default="datetime.datetime.utcnow")
    reps = Column(Integer, server_default="0")              # Total reviews
    lapses = Column(Integer, server_default="0")            # Total times forgotten
    
    # Consolidating legacy metrics into 1 JSON column
    # Stores: {"mdt": {"seen": 0, "correct": 0}, "wrt": {"seen": 0, "correct": 0}}
    next_review_at = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"))
    
    # JSON requires a stringified empty JSON object
    modality_stats = Column(MutableDict.as_mutable(JSON), server_default='{}')

    course = relationship("UserCourse", back_populates="vocabulary")
    reviews = relationship("ReviewLog", back_populates="vocabulary")

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    vocab_id = Column(String(36), ForeignKey("user_vocabulary.id"))
    
    exercise_type = Column(String) # 'mdt', 'wrt', etc.
    # FSRS requires a grade (1-4), not just boolean
    grade = Column(Integer) # 1: Again, 2: Hard, 3: Good, 4: Easy
    speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    vocabulary = relationship("UserVocabulary", back_populates="reviews")