"""
Resume API Endpoints
Handles resume upload, parsing, and analysis with database storage
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, List
import os
import uuid
from pathlib import Path

from app.services.resume_parser import ResumeParser
from app.database import get_db
from app.models.resume import Resume

router = APIRouter()
parser = ResumeParser()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload and parse a resume PDF, then save to database
    
    Args:
        file: PDF file upload
        db: Database session
        
    Returns:
        Parsed resume data with ATS score and suggestions
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    try:
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{file_id}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save uploaded file
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Parse the resume
        result = parser.parse_resume(str(file_path))
        parsed_data = result["parsed_data"]
        
        # Create database record
        resume = Resume(
            id=file_id,
            original_filename=file.filename,
            file_path=str(file_path),
            raw_text=parsed_data.get("raw_text"),
            email=parsed_data.get("email"),
            phone=parsed_data.get("phone"),
            skills=parsed_data.get("skills", []),
            education=parsed_data.get("education", []),
            word_count=parsed_data.get("word_count"),
            ats_score=result.get("ats_score"),
            suggestions=result.get("suggestions", [])
        )
        
        # Save to database
        db.add(resume)
        db.commit()
        db.refresh(resume)
        
        # Return result
        return {
            "status": "success",
            "message": "Resume uploaded and saved to database",
            "resume_id": file_id,
            "original_filename": file.filename,
            "parsed_data": parsed_data,
            "ats_score": result.get("ats_score"),
            "suggestions": result.get("suggestions")
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/{resume_id}")
async def get_resume(resume_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get a resume by ID from database
    
    Args:
        resume_id: UUID of the resume
        db: Database session
        
    Returns:
        Resume data
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {
        "status": "success",
        "resume": resume.to_dict()
    }


@router.get("/")
async def list_resumes(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict:
    """
    List all resumes with pagination
    
    Args:
        limit: Number of results to return
        offset: Number of results to skip
        db: Database session
        
    Returns:
        List of resumes
    """
    resumes = db.query(Resume).order_by(Resume.created_at.desc()).limit(limit).offset(offset).all()
    total = db.query(Resume).count()
    
    return {
        "status": "success",
        "total": total,
        "limit": limit,
        "offset": offset,
        "resumes": [resume.to_dict() for resume in resumes]
    }


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Delete a resume by ID
    
    Args:
        resume_id: UUID of the resume
        db: Database session
        
    Returns:
        Success message
    """
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    # Delete file from disk
    try:
        if os.path.exists(resume.file_path):
            os.remove(resume.file_path)
    except Exception as e:
        print(f"Warning: Could not delete file {resume.file_path}: {e}")
    
    # Delete from database
    db.delete(resume)
    db.commit()
    
    return {
        "status": "success",
        "message": f"Resume {resume_id} deleted"
    }


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "Resume API is working!",
        "parser_status": "initialized",
        "tracked_skills": len(parser.tech_skills),
        "database": "connected"
    }