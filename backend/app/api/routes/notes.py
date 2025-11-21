from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Optional
import shutil
import os
from pathlib import Path
from app.services.document_processor import DocumentProcessor
from app.database.vector_db import vector_db
from app.database.postgres_db import get_db
from app.models.database_models import NotesMetadata
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

router = APIRouter(tags=["notes"])

# Initialize document processor
doc_processor = DocumentProcessor()

# Ensure upload directory exists
UPLOAD_DIR = Path("./data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload")
async def upload_notes(
    file: UploadFile = File(...),
    subject: str = Form(...),
    topic: str = Form(...),
    db: Session = Depends(get_db)
):
    """Upload and process PDF notes"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / stored_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Extract text from PDF
        text_content = doc_processor.extract_text_from_pdf(str(file_path))
        
        if not text_content or len(text_content.strip()) < 50:
            # Delete the file if text extraction failed
            os.remove(file_path)
            raise HTTPException(
                status_code=400, 
                detail="Could not extract enough text from PDF. Make sure it's not scanned/image-based."
            )
        
        # Split into chunks
        chunks = doc_processor.split_text(text_content)
        
        if not chunks:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Failed to process document")
        
        # Prepare data for vector DB
        chunk_ids = [f"{file_id}_chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "file_id": file_id,
                "subject": subject,
                "topic": topic,
                "chunk_index": i,
                "filename": file.filename
            }
            for i in range(len(chunks))
        ]
        
        # Add to vector database
        success = vector_db.add_documents(
            documents=chunks,
            metadatas=metadatas,
            ids=chunk_ids
        )
        
        if not success:
            os.remove(file_path)
            raise HTTPException(status_code=500, detail="Failed to store in vector database")
        
        # Save metadata to PostgreSQL
        try:
            notes_metadata = NotesMetadata(
                file_id=file_id,
                filename=file.filename,
                stored_filename=stored_filename,
                subject=subject,
                topic=topic,
                file_size=file_size,
                file_path=str(file_path),
                chunk_count=len(chunks),
                upload_date=datetime.utcnow()
            )
            
            db.add(notes_metadata)
            db.commit()
            db.refresh(notes_metadata)
            
        except Exception as db_error:
            db.rollback()
            error_msg = str(db_error)
            print(f"Database error: {error_msg}")
            
            # Provide helpful error message
            if "password authentication failed" in error_msg:
                print("⚠️  Database password authentication failed!")
                print("💡 Please check your .env file and update the database password.")
                print("   Run: python fix_database_connection.py to test connection")
            
            # Still return success since vector DB worked
            return {
                "success": True,
                "message": "Notes uploaded to vector DB (metadata save failed)",
                "file_id": file_id,
                "filename": file.filename,
                "subject": subject,
                "topic": topic,
                "chunks_created": len(chunks),
                "warning": "Metadata not saved to PostgreSQL - check database connection"
            }
        
        return {
            "success": True,
            "message": "Notes uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "subject": subject,
            "topic": topic,
            "chunks_created": len(chunks)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/search")
async def search_notes(request: dict):
    """Search notes using vector similarity"""
    try:
        query = request.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Query is required")
        
        # Search in vector database
        results = vector_db.search(query, n_results=5)
        
        if not results or not results.get("documents") or not results["documents"][0]:
            return {
                "success": True,
                "results": [],
                "message": "No relevant notes found"
            }
        
        # Format results
        formatted_results = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else 0
            
            formatted_results.append({
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance  # Convert distance to similarity score
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "count": len(formatted_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/list")
async def list_notes(db: Session = Depends(get_db)):
    """List all uploaded notes"""
    try:
        notes = db.query(NotesMetadata).order_by(NotesMetadata.upload_date.desc()).all()
        return {
            "success": True,
            "notes": [
                {
                    "file_id": note.file_id,
                    "filename": note.filename,
                    "subject": note.subject,
                    "topic": note.topic,
                    "file_size": note.file_size,
                    "upload_date": note.upload_date.isoformat() if note.upload_date else None,
                    "chunk_count": note.chunk_count,
                    "download_url": f"/api/notes/download/{note.file_id}"
                }
                for note in notes
            ],
            "total": len(notes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list notes: {str(e)}")


@router.get("/download/{file_id}")
async def download_note(file_id: str, db: Session = Depends(get_db)):
    """Download a PDF file by file_id"""
    try:
        # Get file metadata from database
        note = db.query(NotesMetadata).filter(
            NotesMetadata.file_id == file_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if file exists
        file_path = Path(note.file_path)
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found on disk")
        
        # Return file for download
        return FileResponse(
            path=str(file_path),
            filename=note.filename,
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@router.get("/topic/{topic}")
async def get_notes_by_topic(topic: str, db: Session = Depends(get_db)):
    """Get all PDFs for a specific topic"""
    try:
        notes = db.query(NotesMetadata).filter(
            NotesMetadata.topic.ilike(f"%{topic}%")
        ).all()
        
        return {
            "success": True,
            "topic": topic,
            "notes": [
                {
                    "file_id": note.file_id,
                    "filename": note.filename,
                    "subject": note.subject,
                    "topic": note.topic,
                    "file_size": note.file_size,
                    "upload_date": note.upload_date.isoformat() if note.upload_date else None,
                    "download_url": f"/api/notes/download/{note.file_id}"
                }
                for note in notes
            ],
            "total": len(notes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get notes by topic: {str(e)}")


@router.delete("/delete/{file_id}")
async def delete_note(file_id: str, db: Session = Depends(get_db)):
    """Delete a note and its associated files"""
    try:
        # Get file metadata
        note = db.query(NotesMetadata).filter(
            NotesMetadata.file_id == file_id
        ).first()
        
        if not note:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete from vector database
        vector_db.delete_by_file_id(file_id)
        
        # Delete file from disk
        file_path = Path(note.file_path)
        if file_path.exists():
            os.remove(file_path)
        
        # Delete from database
        db.delete(note)
        db.commit()
        
        return {
            "success": True,
            "message": "Note deleted successfully",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")