"""
Semantic Job Matching API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.services.semantic_matcher import SemanticMatcher
from app.database import get_db
from app.models.resume import Resume

router = APIRouter()
matcher = SemanticMatcher()


class JobMatchRequest(BaseModel):
    """Request for matching resume to a single job"""
    resume_text: str
    job_description: str
    resume_id: Optional[str] = None
    job_id: Optional[str] = None


class MultiJobMatchRequest(BaseModel):
    """Request for matching resume to multiple jobs"""
    resume_text: str
    jobs: List[dict]  # Each dict should have: id, title, company, description
    resume_id: Optional[str] = None


class ResumeIdMatchRequest(BaseModel):
    """Match using resume ID from database"""
    resume_id: str
    job_description: str


@router.post("/match")
async def match_resume_to_job(request: JobMatchRequest):
    """
    Match a resume to a single job using semantic similarity
    
    Args:
        request: Resume text and job description
        
    Returns:
        Match score and recommendation
    """
    try:
        result = matcher.match_resume_to_job(
            resume_text=request.resume_text,
            job_description=request.job_description,
            resume_id=request.resume_id,
            job_id=request.job_id
        )
        
        return {
            "status": "success",
            "match": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error matching resume to job: {str(e)}"
        )


@router.post("/match-multiple")
async def match_resume_to_multiple_jobs(request: MultiJobMatchRequest):
    """
    Match a resume to multiple jobs and rank them
    
    Args:
        request: Resume text and list of jobs
        
    Returns:
        Ranked list of job matches
    """
    try:
        matches = matcher.match_resume_to_multiple_jobs(
            resume_text=request.resume_text,
            jobs=request.jobs,
            resume_id=request.resume_id
        )
        
        return {
            "status": "success",
            "total_jobs": len(matches),
            "matches": matches
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error matching resume to jobs: {str(e)}"
        )


@router.post("/match-by-id")
async def match_by_resume_id(
    request: ResumeIdMatchRequest,
    db: Session = Depends(get_db)
):
    """
    Match a resume from database to a job
    
    Args:
        request: Resume ID and job description
        db: Database session
        
    Returns:
        Match score and recommendation
    """
    # Get resume from database
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    try:
        result = matcher.match_resume_to_job(
            resume_text=resume.raw_text,
            job_description=request.job_description,
            resume_id=request.resume_id
        )
        
        return {
            "status": "success",
            "resume_id": request.resume_id,
            "resume_filename": resume.original_filename,
            "match": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error matching resume: {str(e)}"
        )


@router.get("/test")
async def test_matching_endpoint():
    """Test endpoint"""
    return {
        "message": "Semantic Matching API is working!",
        "matcher_status": "initialized",
        "model": "all-MiniLM-L6-v2",
        "features": [
            "Single job matching",
            "Multiple job ranking",
            "Resume ID matching"
        ]
    }