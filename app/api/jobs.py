"""
Job Analysis API Endpoints
Analyzes job descriptions and saves results to database
"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.hiring_detector import HiringDetector
from app.database import get_db
from app.models.job_analysis import JobAnalysis

router = APIRouter()
detector = HiringDetector()


class JobAnalysisRequest(BaseModel):
    """Request model for job analysis"""
    job_description: str
    posted_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    

@router.post("/analyze")
async def analyze_job(
    request: JobAnalysisRequest,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Analyze a job posting and save to database
    
    Args:
        request: Job description and optional posting date
        db: Database session
        
    Returns:
        Complete hiring type analysis with application strategy
    """
    try:
        # Analyze the job
        analysis = detector.analyze_hiring_type(
            job_description=request.job_description,
            posted_date=request.posted_date
        )
        
        # Save to database
        job_analysis = JobAnalysis(
            job_description=request.job_description,
            posted_date=request.posted_date,
            hiring_type=analysis["hiring_type"],
            confidence=analysis["confidence"],
            explanation=analysis["explanation"],
            active_score=analysis["active_score"],
            passive_score=analysis["passive_score"],
            red_flag_score=analysis["red_flag_score"],
            active_indicators=analysis["active_indicators"],
            passive_indicators=analysis["passive_indicators"],
            red_flags=analysis["red_flags"],
            requisition_analysis=analysis["requisition_analysis"],
            location_analysis=analysis["location_analysis"],
            specificity_analysis=analysis["specificity_analysis"],
            posting_age_days=analysis["posting_age_days"],
            is_stale=str(analysis["is_stale"]),
            insights=analysis["insights"],
            application_strategy=analysis["application_strategy"]
        )
        
        db.add(job_analysis)
        db.commit()
        db.refresh(job_analysis)
        
        return {
            "status": "success",
            "message": "Job analysis saved to database",
            "analysis_id": job_analysis.id,
            "analysis": analysis
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Error analyzing job posting: {str(e)}"
        )


@router.get("/{analysis_id}")
async def get_job_analysis(analysis_id: str, db: Session = Depends(get_db)) -> Dict:
    """
    Get a job analysis by ID
    
    Args:
        analysis_id: UUID of the analysis
        db: Database session
        
    Returns:
        Job analysis data
    """
    analysis = db.query(JobAnalysis).filter(JobAnalysis.id == analysis_id).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Job analysis not found")
    
    return {
        "status": "success",
        "analysis": analysis.to_dict()
    }


@router.get("/")
async def list_job_analyses(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict:
    """
    List all job analyses with pagination
    
    Args:
        limit: Number of results
        offset: Results to skip
        db: Database session
        
    Returns:
        List of job analyses
    """
    analyses = db.query(JobAnalysis).order_by(JobAnalysis.created_at.desc()).limit(limit).offset(offset).all()
    total = db.query(JobAnalysis).count()
    
    return {
        "status": "success",
        "total": total,
        "limit": limit,
        "offset": offset,
        "analyses": [analysis.to_dict() for analysis in analyses]
    }


@router.get("/test")
async def test_jobs_endpoint():
    """Test endpoint"""
    return {
        "message": "Jobs API is working!",
        "detector_status": "initialized",
        "database": "connected",
        "features": [
            "Job posting analysis",
            "Active vs Pipeline detection",
            "Resume harvesting detection",
            "Application strategy recommendations"
        ]
    }