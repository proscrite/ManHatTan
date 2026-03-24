from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.security import get_current_user
from app.models import generate_uuid

from app.services import parsers 

router = APIRouter(
    prefix="/api/v1/import",
    tags=["Data Ingestion"]
)

@router.post("/document", response_model=dict)
async def import_highlighted_document(
    course_id: str,
    target_color: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Determine platform from file extension
    filename = file.filename.lower()
    if filename.endswith('.docx'):
        platform = 'playbooks'
    elif filename.endswith('.html'):
        platform = 'kindle'
    else:
        raise HTTPException(status_code=400, detail="Only .docx (Play Books) or .html (Kindle) files are supported.")

    # 2. Security Check
    course = db.query(models.UserCourse).filter(
        models.UserCourse.id == course_id, models.UserCourse.user_id == current_user.id
    ).first()
    if not course:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Course not found or you do not have permission to access it."
            )

    try:
        # 3. Pass to our unified parser
        contents = await file.read()
        parsed_data = await parsers.parse_highlighted_document(contents, target_color, course.learning_language, course.ui_language, platform)
        
        # 4. Upsert into database
        records_added = 0
        for item in parsed_data:
            existing = db.query(models.UserVocabulary).filter(
                models.UserVocabulary.course_id == course_id,
                models.UserVocabulary.word_ll == item['word_ll'],
                models.UserVocabulary.word_ul == item['word_ul']
            ).first()
            
            if not existing:
                new_vocab = models.UserVocabulary(
                    id=generate_uuid(), course_id=course_id,
                    word_ul=item['word_ul'], word_ll=item['word_ll'],
                    source_type=item['source_type']
                )
                db.add(new_vocab)
                records_added += 1
                
        db.commit()
        return {"message": f"Successfully translated and imported {records_added} new '{target_color}' highlights from {platform.capitalize()}."}
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/csv", response_model=dict)
async def import_google_translate_csv(
    course_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only .csv files are supported.")

    course = db.query(models.UserCourse).filter(
        models.UserCourse.id == course_id,
        models.UserCourse.user_id == current_user.id
    ).first()
    
    if not course:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Course not found or you do not have permission to access it."
            )

    try:
        # 1. Read bytes into memory
        contents = await file.read()
        
        # 2. Hand off to the Back Office Analyst (parsers.py)
        parsed_data = parsers.parse_google_translate_csv(contents)
        
        records_added = 0
        
        # 3. Database Upsert Logic
        for item in parsed_data:
            # Prevent exact duplicates for this specific course
            existing = db.query(models.UserVocabulary).filter(
                models.UserVocabulary.course_id == course_id,
                models.UserVocabulary.word_ll == item['word_ll'],
                models.UserVocabulary.word_ul == item['word_ul']
            ).first()
            
            if not existing:
                new_vocab = models.UserVocabulary(
                    id=generate_uuid(),
                    course_id=course_id,
                    word_ul=item['word_ul'],
                    word_ll=item['word_ll'],
                    source_type=item['source_type']
                )
                db.add(new_vocab)
                records_added += 1
                
        db.commit()
        return {
            "message": f"Successfully parsed {len(parsed_data)} words. Imported {records_added} new unique words."
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")