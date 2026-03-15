[ ] The "Thin Client" Grading Engine: Update the POST /api/v1/progress/review endpoint. Instead of accepting is_correct, it must accept user_answer (raw text). Implement the grading logic (lowercasing, accent stripping, Levenshtein distance fuzzy matching) in FastAPI.

[ ] Soft Deletes: Add a DELETE /api/v1/vocabulary/{vocab_id} endpoint. Add an is_deleted = Column(Boolean, default=False) field to models.py so users can remove bad imports without destroying historical ML data.

[ ] The ETL Parsing Pipeline: Port your legacy Python scripts (Kindle HTML/Google Play DOCX) into backend/app/services/parsers.py so they return lists of Pydantic schemas for bulk database insertion.

[ ] Authentication Integration: Implement Google Auth via Azure AD B2C (or Firebase). Update FastAPI to require and validate JWTs (JSON Web Tokens) in the HTTP headers before returning any database rows.

[ ] ML Integration (Future): Port the Duolingo HLR model to replace the temporary naive math in the progress router.