from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app import models, schemas
from app.security import get_current_user, get_password_hash
from app.database import get_db

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users & Courses"]
)

@router.post("/users", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.
    """
    # 1. Check if the email is already registered
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email is already registered."
        )
    
    # 2. Hash the raw password
    hashed_pw = get_password_hash(user_in.password)
    
    # 3. Create the SQLAlchemy model instance
    new_user = models.User(
        email=user_in.email,
        name=user_in.name,
        hashed_password=hashed_pw
    )
    
    # 4. Save to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.get("/me/courses", response_model=List[schemas.CourseResponse])
def get_my_courses(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user) # <-- The Bouncer!
):
    """
    Fetches all active courses for the currently authenticated user.
    """
    # We don't need to look up the email anymore.
    # The token already proved who current_user is.
    courses = db.query(models.UserCourse).filter(
        models.UserCourse.user_id == current_user.id,
        models.UserCourse.is_active == True
    ).all()
    
    return courses

@router.post("/me/courses", response_model=schemas.CourseResponse)
def create_my_course(
    # Assuming you have a Pydantic schema for creating a course:
    # class CourseCreate(BaseModel):
    #     learning_language: str
    #     ui_language: str
    course_in: schemas.CourseCreate, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Creates a new course for the currently authenticated user.
    """
    new_course = models.UserCourse(
        user_id=current_user.id,
        learning_language=course_in.learning_language,
        ui_language=course_in.ui_language
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course
