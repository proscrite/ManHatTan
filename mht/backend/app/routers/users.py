from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app import models, schemas
from app.security import get_current_user
from app.database import get_db

router = APIRouter(
    prefix="/api/v1/users",
    tags=["Users & Courses"]
)

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