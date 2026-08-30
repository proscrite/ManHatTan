from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import models            
from app.database import engine   
from app.routers import (multiple_answer, written_input, cloze,
                         vocabulary, progress, users,
                          auth, ingestion, ai)

# Create the SQLite tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Manhattan API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "Project Manhattan is Online"}

app.include_router(vocabulary.router)
app.include_router(users.router)
app.include_router(progress.router)
app.include_router(multiple_answer.router)
app.include_router(written_input.router)
app.include_router(cloze.router)
app.include_router(auth.router)
app.include_router(ingestion.router)

app.include_router(ai.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Manhattan Project Backend!"}