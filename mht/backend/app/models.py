import uuid
from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)

    # Relationships allow you to easily fetch a user's courses
    courses = relationship("UserCourse", back_populates="owner")

class UserCourse(Base):
    __tablename__ = "user_courses"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id = Column(String(36), ForeignKey("users.id"))
    learning_language = Column(String, index=True) # e.g., 'de', 'iw'
    ui_language = Column(String) # e.g., 'en'
    is_active = Column(Boolean, default=True)

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
    p_recall = Column(Float, default=0.0)
    history_seen = Column(Integer, default=0)
    history_correct = Column(Integer, default=0)
    session_seen = Column(Integer, default=0)
    session_correct = Column(Integer, default=0)
    mdt_history = Column(Integer, default=0)
    mdt_correct = Column(Integer, default=0)
    mrt_history = Column(Integer, default=0)
    mrt_correct = Column(Integer, default=0)
    wdt_history = Column(Integer, default=0)
    wdt_correct = Column(Integer, default=0)
    wrt_history = Column(Integer, default=0)
    wrt_correct = Column(Integer, default=0)
    speed = Column(Float, default=0.0)
    next_review_at = Column(DateTime, default=datetime.datetime.utcnow)

    course = relationship("UserCourse", back_populates="vocabulary")
    reviews = relationship("ReviewLog", back_populates="vocabulary")

class ReviewLog(Base):
    __tablename__ = "review_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid, index=True)
    vocab_id = Column(String(36), ForeignKey("user_vocabulary.id"))
    
    exercise_type = Column(String) # 'mdt', 'wrt', etc.
    is_correct = Column(Boolean)
    speed = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    vocabulary = relationship("UserVocabulary", back_populates="reviews")