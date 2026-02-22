"""
Resume API Endpoints
Handles resume upload, parsing, and analysis
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict
import os
import uuid
from pathlib import Path

from app.services.resume_parser import ResumeParser

router = APIRouter()
parser = ResumeParser()

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)) -> Dict:
    """
    Upload and parse a resume PDF
    
    Args:
        file: PDF file upload
        
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
        
        # Add metadata
        result["resume_id"] = file_id
        result["original_filename"] = file.filename
        result["file_path"] = str(file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")


@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "Resume API is working!",
        "parser_status": "initialized",
        "tracked_skills": len(parser.tech_skills)
    }