"""
Cover Letter Generation API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.cover_letter_generator import CoverLetterGenerator

router = APIRouter()
generator = CoverLetterGenerator()


class CoverLetterRequest(BaseModel):
    """Request model for cover letter generation"""
    resume_data: dict
    job_data: dict
    tone: Optional[str] = "professional"


class SimpleCoverLetterRequest(BaseModel):
    """Simplified request using resume ID"""
    resume_id: str
    job_title: str
    company_name: str
    job_description: str
    tone: Optional[str] = "professional"


@router.post("/generate")
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a cover letter from resume and job data
    
    Args:
        request: Resume data, job data, and tone
        
    Returns:
        Generated cover letter text
    """
    try:
        cover_letter = generator.generate_cover_letter(
            resume_data=request.resume_data,
            job_data=request.job_data,
            tone=request.tone
        )
        
        return {
            "status": "success",
            "cover_letter": cover_letter,
            "tone": request.tone,
            "word_count": len(cover_letter.split())
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )


@router.post("/generate-simple")
async def generate_cover_letter_simple(request: SimpleCoverLetterRequest):
    """
    Generate a cover letter with simplified input
    
    Args:
        request: Job details and resume ID
        
    Returns:
        Generated cover letter
    """
    try:
        # For now, we'll create a simple resume structure
        # In production, you'd fetch the actual resume from the database
        resume_data = {
            "contact": {"name": "Candidate"},
            "skills": ["Python", "SQL", "Data Analysis"],
            "experience": []
        }
        
        job_data = {
            "title": request.job_title,
            "company": request.company_name,
            "description": request.job_description
        }
        
        cover_letter = generator.generate_cover_letter(
            resume_data=resume_data,
            job_data=job_data,
            tone=request.tone
        )
        
        return {
            "status": "success",
            "cover_letter": cover_letter,
            "job_title": request.job_title,
            "company": request.company_name,
            "tone": request.tone
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating cover letter: {str(e)}"
        )


@router.get("/test")
async def test_cover_letter_endpoint():
    """Test endpoint"""
    return {
        "message": "Cover Letter API is working!",
        "generator_status": "initialized",
        "available_tones": ["professional", "enthusiastic", "formal"]
    }