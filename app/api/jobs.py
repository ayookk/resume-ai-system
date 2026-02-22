"""
Job Analysis API Endpoints
Analyzes job descriptions for hiring type and provides application strategy
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.hiring_detector import HiringDetector

router = APIRouter()
detector = HiringDetector()


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis"""
    job_description: str
    posted_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    

@router.post("/analyze")
async def analyze_job(request: JobAnalysisRequest):
    """
    Analyze a job posting to determine if it's active hiring or pipeline/evergreen
    
    Args:
        request: Job description and optional posting date
        
    Returns:
        Complete hiring type analysis with application strategy
    """
    try:
        result = detector.analyze_hiring_type(
            job_description=request.job_description,
            posted_date=request.posted_date
        )
        
        return {
            "status": "success",
            "analysis": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing job posting: {str(e)}"
        )


@router.post("/match")
async def match_resume_to_job(resume_id: str, job_description: str):
    """
    Match a resume to a job and provide combined analysis
    (Future enhancement - placeholder for now)
    
    Args:
        resume_id: ID of uploaded resume
        job_description: Job posting text
        
    Returns:
        Match score and hiring type analysis
    """
    # This will be implemented when we add the matching engine
    return {
        "status": "coming_soon",
        "message": "Resume-to-job matching will be implemented in Week 2",
        "resume_id": resume_id,
        "job_preview": job_description[:100] + "..."
    }


@router.get("/test")
async def test_jobs_endpoint():
    """Test endpoint"""
    return {
        "message": "Jobs API is working!",
        "detector_status": "initialized",
        "features": [
            "Job posting analysis",
            "Active vs Pipeline detection",
            "Resume harvesting detection",
            "Application strategy recommendations"
        ]
    }