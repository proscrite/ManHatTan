import random
import datetime
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models import UserVocabulary

def get_next_exercise(db: Session, course_id: str, exclude_ids: List[str] = None, pool_size: int = 10) -> Optional[UserVocabulary]:
    """
    Fetches the next exercise word utilizing a Top-N Shuffle to prevent 
    sequence exploits, while honoring a short-term memory exclusion queue.
    """
    if exclude_ids is None:
        exclude_ids = []
        
    now = datetime.datetime.utcnow()
    
    # 1. Base Query: Fetch words due for this course
    query = db.query(UserVocabulary).filter(
        UserVocabulary.course_id == course_id,
        UserVocabulary.next_review_at <= now
    )

    # 2. Session Queue: Apply the sliding window exclusion
    if exclude_ids:
        query = query.filter(UserVocabulary.id.notin_(exclude_ids))

    # 3. Fetch the top N most urgent words to create our shuffle pool
    due_words_pool = query.order_by(
        UserVocabulary.next_review_at.asc()
    ).limit(pool_size).all()

    # 4. Safe Fallback: If the exclude list blocked all remaining words
    if not due_words_pool and exclude_ids:
        due_words_pool = db.query(UserVocabulary).filter(
            UserVocabulary.course_id == course_id,
            UserVocabulary.next_review_at <= now
        ).order_by(
            UserVocabulary.next_review_at.asc()
        ).limit(pool_size).all()

    # 5. Return weak words if queue is empty
    if not due_words_pool:
        # Fallback to the weakest words available
        return db.query(UserVocabulary).filter(
            UserVocabulary.course_id == course_id
        ).order_by(UserVocabulary.fsrs_stability.asc()).first()

    return random.choice(due_words_pool)