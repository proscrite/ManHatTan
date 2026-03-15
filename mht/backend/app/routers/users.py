from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app import models, schemas

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users & Courses"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{email}/courses", response_model=List[schemas.CourseResponse])
def get_user_courses_by_email(email: str, db: Session = Depends(get_db)):
    """
    Fetches all active courses for a user based on their email.
    """
    # 1. Find the user by email
    user = db.query(models.User).filter(models.User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 2. Find their courses
    courses = db.query(models.UserCourse).filter(
        models.UserCourse.user_id == user.id,
        models.UserCourse.is_active == True
    ).all()
    
    return courses