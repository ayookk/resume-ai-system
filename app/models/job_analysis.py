"""
Job Analysis database model
"""
from sqlalchemy import Column, String, Float, Text, DateTime, JSON, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid


class JobAnalysis(Base):
    __tablename__ = "job_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Job information
    job_description = Column(Text, nullable=False)
    posted_date = Column(String)  # ISO format date string
    
    # Analysis results
    hiring_type = Column(String)  # "Active Hiring", "Pipeline/Evergreen", etc.
    confidence = Column(String)  # "High", "Medium", "Low"
    explanation = Column(Text)
    
    # Scores
    active_score = Column(Integer)
    passive_score = Column(Integer)
    red_flag_score = Column(Integer)
    
    # Detailed analysis (stored as JSON)
    active_indicators = Column(JSON)
    passive_indicators = Column(JSON)
    red_flags = Column(JSON)
    requisition_analysis = Column(JSON)
    location_analysis = Column(JSON)
    specificity_analysis = Column(JSON)
    
    # Additional metadata
    posting_age_days = Column(Integer)
    is_stale = Column(String)  # "true" or "false" as string
    
    # Insights and strategy (stored as JSON arrays)
    insights = Column(JSON)
    application_strategy = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "analysis_id": self.id,
            "job_description": self.job_description[:200] + "..." if len(self.job_description) > 200 else self.job_description,
            "posted_date": self.posted_date,
            "hiring_type": self.hiring_type,
            "confidence": self.confidence,
            "explanation": self.explanation,
            "active_score": self.active_score,
            "passive_score": self.passive_score,
            "red_flag_score": self.red_flag_score,
            "insights": self.insights,
            "application_strategy": self.application_strategy,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }