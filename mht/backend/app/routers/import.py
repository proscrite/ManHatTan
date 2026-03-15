@app.post("/api/v1/import/kindle")
async def import_kindle(file: UploadFile, db: Session = Depends(get_db)):
    # 1. Read the uploaded file into memory (No saving to disk!)
    content = await file.read()
    
    # 2. Extract & Transform (Returns list of Pydantic schemas)
    parsed_words = parse_kindle_html(content) 
    
    # 3. Load (Bulk inserts into SQLite)
    import_result = save_vocabulary_to_db(db, parsed_words)
    
    return {"message": f"Successfully imported {import_result} words!"}