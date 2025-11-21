import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import chat, notes, results, syllabus

app = FastAPI(title="College AI Assistant API")

# Add CORS middleware
# Get allowed origins from environment variable or default to localhost
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api")
app.include_router(notes.router, prefix="/api/notes")
app.include_router(results.router, prefix="/api/results")
app.include_router(syllabus.router, prefix="/api/syllabus")

@app.get("/")
async def root():
    return {"message": "College AI Assistant API is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}