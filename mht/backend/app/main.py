from fastapi import FastAPI
from app import models            
from app.database import engine   
from app.routers import vocabulary, progress, users

# Create the SQLite tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Manhattan API")

# Plug the router into the main application
app.include_router(vocabulary.router)
app.include_router(users.router)
app.include_router(progress.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Manhattan Project Backend!"}